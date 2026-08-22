import pytest
from app.services.guard_service import evaluate_candidate

def test_guard_rejects_wolf_for_fox_post():
    """PROBE 3: Force the wolf as a candidate for the fox post -> REJECT"""
    decision = evaluate_candidate(
        post_subject="red fox",
        image_subject="gray wolf",
        similarity_score=0.85, # High similarity, but guard must catch the subject mismatch
        vision_confidence=0.95
    )
    assert decision.verdict == "reject"
    assert decision.reason_code == "category_mismatch"
    assert "red fox" in decision.explanation and "gray wolf" in decision.explanation

def test_guard_handles_synonyms():
    """Ensure Vulpes vulpes maps to red fox and doesn't get rejected"""
    decision = evaluate_candidate(
        post_subject="red fox",
        image_subject="vulpes vulpes",
        similarity_score=0.88,
        vision_confidence=0.92
    )
    assert decision.verdict == "suggest"

def test_no_confident_match():
    """PROBE 4: Post with no suitable image -> no_confident_match"""
    decision = evaluate_candidate(
        post_subject="red fox",
        image_subject="red fox",
        similarity_score=0.20, # Way below threshold
        vision_confidence=0.90
    )
    assert decision.verdict == "no_confident_match"
    assert decision.reason_code == "similarity_below_threshold"

def test_low_vision_confidence_flags():
    """Image matches, but vision model was unsure -> flag_for_review"""
    decision = evaluate_candidate(
        post_subject="red fox",
        image_subject="red fox",
        similarity_score=0.80,
        vision_confidence=0.50 # Below 0.70 floor
    )
    assert decision.verdict == "flag_for_review"
    assert decision.reason_code == "low_vision_confidence"

def test_perfect_match():
    decision = evaluate_candidate(
        post_subject="gray wolf",
        image_subject="gray wolf",
        similarity_score=0.89,
        vision_confidence=0.95
    )
    assert decision.verdict == "suggest"
    assert decision.reason_code == "match"