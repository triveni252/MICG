from huggingface_hub import InferenceClient
import sys

try:
    print("Testing Mistral...")
    client = InferenceClient() # No token
    res = client.text_generation(
        "Generate 1 creative caption for a dog running.",
        model="mistralai/Mistral-7B-Instruct-v0.2",
        max_new_tokens=50
    )
    print("Success:", res)
    sys.exit(0)
except Exception as e:
    print("Error:", e)
    sys.exit(1)
