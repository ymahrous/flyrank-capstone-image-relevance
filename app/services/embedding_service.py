import os
from google import genai
import logging

logger = logging.getLogger(__name__)

# Initialize the modern client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a given text string."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
    )
    return result.embeddings[0].values

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculates cosine similarity between two vectors."""
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be same length")
    
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

# Need to import types for the embed config
from google.genai import types