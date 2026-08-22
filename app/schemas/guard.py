from pydantic import BaseModel
from typing import Literal

class GuardDecision(BaseModel):
    # Distinguish between "this specific image is wrong" vs "no image is good enough"
    verdict: Literal["suggest", "flag_for_review", "reject", "no_confident_match"]
    reason_code: str  # e.g., "category_mismatch", "similarity_below_threshold"
    explanation: str
    similarity_score: float