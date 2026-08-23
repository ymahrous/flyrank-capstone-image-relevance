import os
from dotenv import load_dotenv
load_dotenv()

from google import genai
from app.schemas.metadata import PostMetadata
import logging

logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in .env file!")

client = genai.Client(api_key=api_key)

EXTRACT_PROMPT = """Analyze this blog post text and return a JSON object with exactly these fields:
- "subject": The main topic, lowercase (e.g., "red fox", "gray wolf", "labrador dog")
- "category": Exactly one of: "animal", "landscape", "food", "object", "building"
Return ONLY valid JSON."""

async def extract_post_metadata(content: str) -> PostMetadata:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=EXTRACT_PROMPT + "\n\nText: " + content
    )
    raw_text = response.text.strip()
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0]
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0]
    return PostMetadata.model_validate_json(raw_text)