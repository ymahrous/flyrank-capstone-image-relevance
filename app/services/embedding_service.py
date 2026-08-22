import os
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini's free-tier embedding model
EMBEDDING_MODEL = "models/gemini-embedding-001"

async def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a given text string."""
    result = await genai.embed_content_async(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="SEMANTIC_SIMILARITY"
    )
    return result['embedding']

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