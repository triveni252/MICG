from dotenv import load_dotenv
load_dotenv()
import os
from huggingface_hub import InferenceClient

token = os.getenv("HF_TOKEN")
try:
    print("Testing Mistral conversational...")
    client = InferenceClient(token=token)
    res = client.chat_completion(
        messages=[{"role": "user", "content": "Generate 1 creative caption for a dog running."}],
        model="mistralai/Mistral-7B-Instruct-v0.2",
        max_tokens=50
    )
    print("Success:", res.choices[0].message.content)
except Exception as e:
    print("Error:", e)
