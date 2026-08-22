import logging
from app.schemas.guard import GuardDecision

logger = logging.getLogger(__name__)

# Thresholds - We will tune these in Step 6!
SIMILARITY_THRESHOLD = 0.50
CONFIDENCE_FLOOR = 0.70

# A small controlled vocabulary map to handle synonyms like "Vulpes vulpes" -> "fox"
SYNONYM_MAP = {
    "vulpes vulpes": "red fox",
    "canis lupus": "gray wolf",
    "canis familiaris": "dog",
    "canis lupus familiaris": "dog"
}

def normalize_subject(subject: str) -> str:
    subject = subject.lower().strip()
    return SYNONYM_MAP.get(subject, subject)

def evaluate_candidate(
    post_subject: str, 
    image_subject: str, 
    similarity_score: float, 
    vision_confidence: float
) -> GuardDecision:
    """The 3-signal safety guard."""
    
    norm_post = normalize_subject(post_subject)
    norm_img = normalize_subject(image_subject)
    
    # SIGNAL 1: Hard Subject Veto
    # If the core subjects don't share a root word, reject immediately.
    # e.g., "fox" and "wolf" share no root.
    post_words = set(norm_post.split())
    img_words = set(norm_img.split())
    
    if not post_words.intersection(img_words):
        return GuardDecision(
            verdict="reject",
            reason_code="category_mismatch",
            explanation=f"Subject mismatch: expected '{norm_post}', detected '{norm_img}'",
            similarity_score=similarity_score
        )
        
    # SIGNAL 2: Similarity Threshold
    if similarity_score < SIMILARITY_THRESHOLD:
        return GuardDecision(
            verdict="no_confident_match",
            reason_code="similarity_below_threshold",
            explanation=f"Semantic similarity ({similarity_score:.2f}) is below the safety threshold ({SIMILARITY_THRESHOLD})",
            similarity_score=similarity_score
        )
        
    # SIGNAL 3: Vision Confidence Floor
    if vision_confidence < CONFIDENCE_FLOOR:
        return GuardDecision(
            verdict="flag_for_review",
            reason_code="low_vision_confidence",
            explanation=f"Vision model confidence ({vision_confidence:.2f}) is too low to auto-suggest",
            similarity_score=similarity_score
        )
        
    # PASSED ALL GUARDS
    return GuardDecision(
        verdict="suggest",
        reason_code="match",
        explanation=f"Strong match. Subject '{norm_img}' aligns with post topic '{norm_post}' (Sim: {similarity_score:.2f})",
        similarity_score=similarity_score
    )