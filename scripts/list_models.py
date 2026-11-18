from google import genai

# Creates a client. It reads the key from GEMINI_API_KEY automatically,
# so the key never appears in your code.
client = genai.Client()

# Ask the API for every model this key can use,
# and print only the "flash" ones (fast, cheap, good for SQL).
for m in client.models.list():
    if "flash" in m.name:
        print(m.name)