import os
from google import genai
from google.genai import types
from app.schemas.metadata import ImageMetadata
import logging

logger = logging.getLogger(__name__)

# Initialize the modern client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
    try:
        # Use the modern generate_content method
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-05-20',
            contents=[PROMPT, types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')]
        )
        
        raw_text = response.text
        
        # Gemini sometimes wraps JSON in ```json ... ``` blocks. Strip it.
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.split("\n", 1)[1]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
                
        # Strict Pydantic validation
        metadata = ImageMetadata.model_validate_json(cleaned_text)
        
        return metadata, raw_text
        
    except Exception as e:
        logger.error(f"Vision parsing failed: {e}")
        return None, raw_text if 'raw_text' in locals() else str(e)