import os
from google import genai
from app.schemas.metadata import PostMetadata
import logging

logger = logging.getLogger(__name__)

# Initialize the modern client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EXTRACT_PROMPT = """
Analyze this blog post text and return a JSON object with exactly these fields:
- "subject": The main topic, lowercase (e.g., "red fox", "gray wolf", "labrador dog")
- "category": Exactly one of: "animal", "landscape", "food", "object", "building"
Return ONLY valid JSON.
"""

async def extract_post_metadata(content: str) -> PostMetadata:
    response = client.models.generate_content(
        model='gemini-2.5-flash-preview-05-20',
        contents=EXTRACT_PROMPT + "\n\nText: " + content
    )
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1].replace("```", "")
        
    return PostMetadata.model_validate_json(raw_text)