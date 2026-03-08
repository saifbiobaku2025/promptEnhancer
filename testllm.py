import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    messages=[{"role": "user", "content": "Say hello"}],
    max_tokens=50
)

print(response.choices[0].message.content)