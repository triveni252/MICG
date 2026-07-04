import os
import io
import json
import logging
import re
from typing import List, Dict
from PIL import Image
from difflib import SequenceMatcher
from groq import Groq
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
# ── Model Constants ────────────────────────────────────────────────────────────
BLIP_MODEL_NAME = "Salesforce/blip-image-captioning-large"
GROQ_MODEL      = "llama-3.1-8b-instant"
 
# ── Global model cache ─────────────────────────────────────────────────────────
_blip_processor = None
_blip_model     = None
_groq_client    = None
 
 
def preload_models():
    """Called on startup — loads BLIP locally into memory."""
    global _blip_processor, _blip_model
    try:
        logger.info("⏳ Loading BLIP model locally...")
        from transformers import BlipProcessor, BlipForConditionalGeneration
        import torch
 
        _blip_processor = BlipProcessor.from_pretrained(BLIP_MODEL_NAME)
        _blip_model = BlipForConditionalGeneration.from_pretrained(
            BLIP_MODEL_NAME,
            torch_dtype=torch.float32,
        )
        _blip_model.eval()
        logger.info("✅ BLIP model loaded and ready!")
    except Exception as e:
        logger.error(f"❌ Failed to load BLIP model: {e}")
 
 
def _get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        token = os.getenv("GROQ_API_KEY")
        if not token:
            raise RuntimeError("GROQ_API_KEY environment variable is not set.")
        _groq_client = Groq(api_key=token)
    return _groq_client
 
 
# ── Helpers ────────────────────────────────────────────────────────────────────
 
def calculate_relevance_score(base: str, caption: str) -> int:
    ratio = SequenceMatcher(None, base.lower(), caption.lower()).ratio()
    return int(ratio * 100)
 
 
def _extract_json_array(text: str):
    """Robustly extract a JSON array from LLM output."""
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
    lines = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', text)
    if lines:
        return lines
    raise ValueError(f"Could not parse JSON from: {text[:200]}")
 
 
def _prepare_image(image_bytes: bytes) -> Image.Image:
    """Resize and convert image for BLIP processing."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image.thumbnail((384, 384), Image.LANCZOS)
    return image
 
 
# ── Stage 1: Local BLIP Vision ─────────────────────────────────────────────────
 
def generate_base_caption(image_bytes: bytes) -> str:
    """Use locally loaded BLIP model to describe the image."""
    global _blip_processor, _blip_model
 
    if _blip_processor is None or _blip_model is None:
        logger.warning("BLIP not loaded, loading now...")
        preload_models()
 
    if _blip_processor is None or _blip_model is None:
        logger.error("BLIP model unavailable!")
        return None
 
    try:
        import torch
 
        image = _prepare_image(image_bytes)
 
        inputs = _blip_processor(
            images=image,
            text="a photograph of",
            return_tensors="pt",
            padding=True,
        )
 
        with torch.no_grad():
            output = _blip_model.generate(
                **inputs,
                max_new_tokens=50,
                num_beams=4,
                early_stopping=True,
            )
 
        caption = _blip_processor.decode(output[0], skip_special_tokens=True).strip()
 
        if caption.lower().startswith("a photograph of"):
            caption = caption[len("a photograph of"):].strip()
 
        if caption and len(caption) > 5:
            logger.info(f"✅ Local BLIP caption: {caption}")
            return caption
        else:
            logger.warning(f"BLIP short/empty: '{caption}'")
            return None
 
    except Exception as e:
        logger.error(f"❌ Local BLIP error: {e}")
        return None
 
 
# ── Stage 2: Groq LLM Caption Generation ──────────────────────────────────────
 
def generate_llm_captions(
    insight: str,
    mood: str,
    language: str,
    style: str,
    count: int = 5,
) -> List[str]:
    """Use Groq Llama to generate diverse, mood-aware captions."""
 
    style_guide = {
        "casual":   "Write in a relaxed, conversational, everyday tone.",
        "poetic":   "Use metaphors, imagery, and lyrical language.",
        "formal":   "Use professional, polished, and structured language.",
        "hashtag":  "End with 3-5 relevant hashtags. Keep caption short.",
        "quote":    "Write as an inspirational or thought-provoking quote.",
    }
 
    mood_guide = {
        "calm":          "Peaceful, serene, slow-paced tone.",
        "happy":         "Joyful, upbeat, cheerful, positive energy.",
        "sad":           "Melancholic, reflective, bittersweet tone.",
        "romantic":      "Warm, loving, tender, intimate tone.",
        "humorous":      "Witty, funny, lighthearted, playful tone.",
        "inspirational": "Motivating, uplifting, empowering tone.",
        "mysterious":    "Intriguing, suspenseful, thought-provoking tone.",
        "dramatic":      "Intense, bold, powerful, emotional tone.",
        "fun":           "Playful, energetic, exciting tone.",
        "accurate":      "Factual, descriptive, precise, no embellishment.",
        "serious":       "Thoughtful, composed, no humor.",
        "formal":        "Professional, respectful, structured.",
        "professional":  "Business-appropriate, clear, confident.",
        "excited":       "Enthusiastic, high-energy, expressive.",
        "adventurous":   "Bold, daring, exploratory tone.",
        "relaxed":       "Laid-back, easygoing, comfortable tone.",
        "alt_text":      "Descriptive, accessibility-focused, factual.",
        "filename":      "Short, lowercase, hyphen-separated words only.",
        "joke":          "Funny, punny, humorous twist on the image.",
    }
 
    style_hint = style_guide.get(style, "Write naturally and creatively.")
    mood_hint  = mood_guide.get(mood, f"Capture a {mood} feeling.")
 
    prompt = f"""You are an expert social media copywriter and creative caption specialist.
 
IMAGE DESCRIPTION: "{insight}"
 
Generate exactly {count} unique captions for this image.
 
REQUIREMENTS:
- Mood: {mood} ({mood_hint})
- Style: {style} ({style_hint})
- Language: Write ALL captions in {language} ONLY. Use native script for non-English languages (Telugu script for Telugu, Devanagari for Hindi, etc.)
- Each caption must be completely different in structure and vocabulary.
- Must relate directly to the image description above.
- No generic filler phrases like "beautiful image" or "stunning view".
- Length: 1-3 sentences per caption.
 
Return ONLY a JSON array of {count} strings. No explanation, no markdown.
["caption1", "caption2", "caption3", "caption4", "caption5"]"""
 
    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative caption writer. Always respond with only a valid JSON array of strings."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.85,
            max_tokens=900,
        )
 
        raw = response.choices[0].message.content.strip()
        logger.info(f"✅ Groq output: {raw[:300]}")
        captions = _extract_json_array(raw)
        captions = [c.strip() for c in captions if isinstance(c, str) and len(c.strip()) > 5]
        return captions[:count]
 
    except Exception as e:
        logger.error(f"❌ Groq API error: {e}")
        return []
 
 
# ── Main Pipeline ──────────────────────────────────────────────────────────────
 
def run_pipeline(image_bytes: bytes, mood: str, language: str, style: str) -> Dict:
    """
    Full pipeline:
      1. Local BLIP  → accurate visual description of image
      2. Groq Llama  → 5 diverse mood/language/style captions
    """
    mood     = (mood     or "calm").strip()
    style    = (style    or "casual").strip()
    language = (language or "English (US)").strip()
 
    # ── Stage 1: BLIP Vision ──
    insight = generate_base_caption(image_bytes)
 
    if not insight:
        insight_for_llm = "an interesting photograph"
        insight_display = "Image analysis unavailable."
    else:
        insight_for_llm = insight
        insight_display = insight
 
    # ── Stage 2: Groq LLM ──
    caption_texts = generate_llm_captions(
        insight_for_llm, mood, language, style, count=5
    )
 
    # ── Fallback ──
    if not caption_texts:
        caption_texts = [
            insight_for_llm,
            f"A {mood} moment — {insight_for_llm}",
            f"Captured beautifully: {insight_for_llm}",
            f"Every picture tells a story: {insight_for_llm}",
            f"A moment in time: {insight_for_llm}",
        ]
 
    captions = []
    for text in caption_texts:
        captions.append({
            "text":            text,
            "mood":            mood,
            "language":        language,
            "style":           style,
            "relevance_score": calculate_relevance_score(insight_for_llm, text),
        })
 
    return {
        "insight":  insight_display,
        "captions": captions,
    }