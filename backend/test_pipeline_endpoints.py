from dotenv import load_dotenv
load_dotenv()
import os
import io
import urllib.request
from PIL import Image
from huggingface_hub import InferenceClient

token = os.getenv("HF_TOKEN")
client = InferenceClient(token=token)

print("Downloading test image...")
urllib.request.urlretrieve("https://picsum.photos/400/300", "test.jpg")
with open("test.jpg", "rb") as f:
    image_bytes = f.read()

print("Testing Vision Model...")
try:
    res = client.image_to_text(image_bytes, model="Salesforce/blip-image-captioning-large")
    print("Vision Success:", res)
    if isinstance(res, list) and len(res) > 0 and 'generated_text' in res[0]:
        base_caption = res[0]['generated_text']
    elif hasattr(res, 'generated_text'):
        base_caption = res.generated_text
    elif isinstance(res, str):
        base_caption = res
    else:
        base_caption = str(res)
except Exception as e:
    print("Vision Error:", type(e).__name__, "-", e)
    base_caption = "A scenic and beautiful image"

print(f"\nExtracted Base Caption: {base_caption}\n")

print("Testing LLM...")
prompt = f"""<s>[INST] You are an expert social media manager and creative writer.
I have an image with this exact description: "{base_caption}"

Task: Generate exactly 5 highly creative, completely distinct, and significantly varied captions for this image. Do NOT simply repeat the original description.
Constraints:
- Mood/Emotion: happy
- Format/Style: poetic
- Output Language: English (US) (You MUST write the 5 captions strictly in this language)

Response format: Output ONLY a valid JSON array of 5 strings. No markdown formatting, no intro, no explanations. 
Example: ["Caption one", "Caption two", "Caption three", "Caption four", "Caption five"]
[/INST]"""

try:
    res = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model="mistralai/Mistral-7B-Instruct-v0.2",
        max_tokens=800,
        temperature=0.85,
        top_p=0.9
    )
    print("LLM Success:", res.choices[0].message.content)
except Exception as e:
    print("LLM Error:", type(e).__name__, "-", e)
