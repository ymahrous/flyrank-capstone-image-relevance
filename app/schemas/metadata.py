from pydantic import BaseModel, Field
from typing import Literal

# Controlled vocabulary is crucial for the mismatch guard later
VALID_CATEGORIES = Literal["animal", "landscape", "food", "object", "building"]

class ImageMetadata(BaseModel):
    subject: str = Field(..., max_length=100, description="Normalized lowercase subject, e.g., 'red fox'")
    category: VALID_CATEGORIES
    attributes: list[str] = Field(..., max_length=8, description="Visual attributes like 'orange fur', 'forest'")
    caption: str = Field(..., max_length=300)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model's own certainty score")

class PostMetadata(BaseModel):
    subject: str = Field(..., max_length=100, description="Main topic extracted from text")
    category: VALID_CATEGORIES