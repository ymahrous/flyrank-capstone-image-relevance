import os
import base64
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from app.schemas.metadata import ImageMetadata
import logging

logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in .env file!")
client = genai.Client(api_key=api_key)

PROMPT = """
Analyze this image and return a JSON object with exactly these fields:
- "subject": The main subject, lowercase (e.g., "red fox", "gray wolf", "golden retriever")
- "category": Exactly one of: "animal", "landscape", "food", "object", "building"
- "attributes": A list of 3 to 5 visual attributes (e.g., ["orange fur", "forest background", "standing"])
- "caption": A one-sentence factual caption of the image.
- "confidence": A float between 0.0 and 1.0 indicating how confident you are in the subject classification.
Return ONLY valid JSON, no other text.
"""

async def analyze_image(image_bytes: bytes) -> tuple[ImageMetadata | None, str]:
    raw_text = ""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_text(text=PROMPT),
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            ]
        )
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0]
        metadata = ImageMetadata.model_validate_json(raw_text)
        return metadata, raw_text
    except Exception as e:
        logger.error(f"Vision parsing failed: {e}")
        return None, raw_text or str(e)