from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import Post, PostVector, ImageVector, Image, ImageMetadataRecord, Suggestion
from app.services.embedding_service import cosine_similarity, get_embedding
from app.services.guard_service import evaluate_candidate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/matching", tags=["matching"])

@router.get("/posts/{post_id}/images")
async def get_suggestions(post_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Get Post Data
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    post_vec_record = await db.execute(select(PostVector).where(PostVector.post_id == post_id))
    post_vec = post_vec_record.scalar_one_or_none()
    if not post_vec:
        raise HTTPException(status_code=400, detail="Post not embedded yet")
        
    # 2. Get ALL image vectors
    img_vecs_result = await db.execute(select(ImageVector))
    all_img_vecs = img_vecs_result.scalars().all()
    
    if not all_img_vecs:
        return {"message": "No images in the system yet."}

    # 3. Rank by Cosine Similarity
    scored_candidates = []
    for img_vec in all_img_vecs:
        sim_score = cosine_similarity(post_vec.embedding, img_vec.embedding)
        scored_candidates.append({"image_id": img_vec.image_id, "similarity": sim_score})
        
    # Sort highest to lowest
    scored_candidates.sort(key=lambda x: x["similarity"], reverse=True)
    
    # 4. Run the Guard on Top 3 Candidates
    results = []
    top_suggestion = None
    
    for cand in scored_candidates[:3]:
        img_meta = await db.execute(select(ImageMetadataRecord).where(ImageMetadataRecord.image_id == cand["image_id"]))
        meta = img_meta.scalar_one()
        
        decision = evaluate_candidate(
            post_subject=post.subject,
            image_subject=meta.subject,
            similarity_score=cand["similarity"],
            vision_confidence=meta.confidence
        )
        
        results.append({
            "image_id": cand["image_id"],
            "subject": meta.subject,
            "similarity": cand["similarity"],
            "guard_decision": decision.verdict,
            "explanation": decision.explanation
        })
        
        # Save the first "suggest" for the DB
        if decision.verdict == "suggest" and not top_suggestion:
            top_suggestion = cand["image_id"]

    # 5. Handle "No Confident Match" at the top level
    if not top_suggestion:
        # Find out why
        reasons = [r["explanation"] for r in results if r["guard_decision"] == "reject" or r["guard_decision"] == "no_confident_match"]
        return {
            "post_id": post_id,
            "suggestion": None,
            "verdict": "no_confident_match",
            "explanation": "No suitable image found. " + "; ".join(reasons[:2]),
            "candidates_evaluated": results
        }

    # 6. Save Suggestion to DB for the review trail
    new_suggestion = Suggestion(
        post_id=post_id,
        image_id=top_suggestion,
        similarity=results[0]["similarity"],
        verdict="suggest",
        reason_code="match",
        explanation=results[0]["explanation"],
        status="pending"
    )
    db.add(new_suggestion)
    await db.commit()

    return {
        "post_id": post_id,
        "suggestion": results[0],
        "verdict": "suggest",
        "candidates_evaluated": results
    }