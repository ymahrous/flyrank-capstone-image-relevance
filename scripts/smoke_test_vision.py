import os
import google.generativeai as genai
from PIL import Image
import io
import requests

# Load key from .env (you'd typically use python-dotenv, but keeping it simple)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Download a tiny test image
url = "https://images.unsplash.com/photo-1474511320723-9a56873571b7?w=100&q=80" # Fox
response = requests.get(url)
img = Image.open(io.BytesIO(response.content))

# Initialize model
model = genai.GenerativeModel('gemini-1.5-flash')

# Run simplest possible vision call
response = model.generate_content(
    ["What is in this image? Reply in one word.", img]
)

print("--- VISION SMOKE TEST SUCCESS ---")
print(f"Response: {response.text}")
print("---------------------------------")