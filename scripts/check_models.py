import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Checking available models for your API key...\n")

for m in genai.list_models():
    # We only care about models that can generate content (not just embed)
    if 'generateContent' in m.supported_generation_methods:
        print(f"Name: {m.name:45} | Methods: {m.supported_generation_methods}")

