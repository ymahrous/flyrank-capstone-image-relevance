import os
import google.generativeai as genai
from PIL import Image
import io
import requests

# Load key from environment
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Unsplash requires a User-Agent header, otherwise it blocks the request
url = "https://images.unsplash.com/photo-1474511320723-9a56873571b7?w=256&q=80"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content))
except Exception as e:
    print(f"Failed to download image: {e}")
    print("Using a local solid-color fallback image for the smoke test...")
    # Create a tiny 50x50 red image in memory as a fallback
    img = Image.new("RGB", (50, 50), color="red")

# Initialize model
model = genai.GenerativeModel('gemini-1.5-flash')

# Run simplest possible vision call
response = model.generate_content(
    ["What is in this image? Reply in one word.", img]
)

print("--- VISION SMOKE TEST SUCCESS ---")
print(f"Response: {response.text}")
print("---------------------------------")