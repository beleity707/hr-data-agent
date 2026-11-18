import os
import time
from google import genai
from google.genai import errors

client = genai.Client()

# 1) SETTINGS: primary model first, then fallbacks.
MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]


# 2) FUNCTION: must be defined BEFORE it is used.
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


# 3) MAIN CODE: runs last, so ask() already exists.
schema = """
employees(employee_id, first_name, last_name, country, org_unit_id,
          job_title, job_level, manager_id, hire_date, exit_date, status)
org_units(org_unit_id, name, parent_org_unit_id)
"""

questions = [
    "How many active employees are there in each country?",
    "Which 3 countries have the most employees who left?",
    "Average job level per department name",
]

for q in questions:
    prompt = f"""You write SQLite queries.
Schema:
{schema}
Return ONLY the SQL query, no explanation, no markdown.
Question: {q}"""
    print(f"\nQ: {q}")
    print(ask(prompt))