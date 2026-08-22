import os
import json
import google.generativeai as genai
from app.schemas.metadata import ImageMetadata
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Using the model that works on your free tier
model = genai.GenerativeModel('gemini-pro-vision')

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
    """
    Returns a tuple: (Parsed_Metadata_or_None, raw_response_text)
    """
    from google.generativeai import Image as GenImage
    
    img = GenImage.from_bytes(image_bytes)
    
    try:
        response = await model.generate_content_async([PROMPT, img])
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
        # Return the raw text so the job can log what went wrong
        return None, raw_text if 'raw_text' in locals() else str(e)
