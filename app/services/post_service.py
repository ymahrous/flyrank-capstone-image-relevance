import os
import google.generativeai as genai
import logging
from app.schemas.metadata import PostMetadata

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# UPDATED: Using standard flash for text-only extraction
model = genai.GenerativeModel('gemini-2.5-flash')

EXTRACT_PROMPT = """
Analyze this blog post text and return a JSON object with exactly these fields:
- "subject": The main topic, lowercase (e.g., "red fox", "gray wolf", "labrador dog")
- "category": Exactly one of: "animal", "landscape", "food", "object", "building"
Return ONLY valid JSON.
"""

async def extract_post_metadata(content: str) -> PostMetadata:
    response = await model.generate_content_async([EXTRACT_PROMPT, content])
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1].replace("```", "")
        
    return PostMetadata.model_validate_json(raw_text)