import os
import time
from google import genai
from google.genai import errors

client = genai.Client()

# Primary model first, then fallbacks.
MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
    "gemini-2.5-flash",
    "gemini-3.8-flash",
]


def ask(prompt, retries_per_model=3):
    """Try each model in turn; retry temporary errors (429/503) with exponential backoff."""
    for model in MODELS:
        delay = 2
        for attempt in range(1, retries_per_model + 1):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                print(f"Answered by: {model}")
                return response.text
            except (errors.ServerError, errors.ClientError) as e:
                if getattr(e, "code", None) not in (429, 503):
                    raise
                print(f"{model} attempt {attempt} failed ({e.code}). Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
        print(f"Switching from {model} to the next model...")
    raise RuntimeError("All models unavailable - try again later.")


print(ask("In one sentence, what does an HR analytics team do?"))