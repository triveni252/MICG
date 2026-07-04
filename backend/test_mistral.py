from huggingface_hub import InferenceClient
import json

base_caption = "two men riding a scooter"
mood = "happy"
style = "poetic"
language = "Telugu"

prompt = f"""<s>[INST] You are an expert social media manager and copywriter.
I have an image described as: "{base_caption}"

Task: Generate exactly 5 highly creative, completely distinct and significantly varied captions for this image. None of the captions should be a simple repeat of the base description.
Constraints:
- Mood/Emotion: {mood}
- Style/Format: {style}
- Output Language: {language} (You MUST write the captions in this language)

You must output ONLY a raw JSON array of 5 strings. No markdown formatting, no explanations. Just the array.
[/INST]"""

try:
    client = InferenceClient()
    res = client.text_generation(
        prompt,
        model="mistralai/Mistral-7B-Instruct-v0.2",
        max_new_tokens=500,
        temperature=0.8,
        top_p=0.9
    )
    text = res.strip()
    print("RAW OUTPUT:", text)
    try:
        parsed = json.loads(text)
        print("PARSED:", parsed)
    except Exception as e:
        print("JSON parse failed:", e)
except Exception as e:
    print("Error calling API:", e)
