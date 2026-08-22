import os
import json
import asyncio
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import Post, PostVector, ImageVector, Image, ImageMetadataRecord
from app.services.embedding_service import cosine_similarity
from app.services.guard_service import evaluate_candidate

EVAL_SET_PATH = "app/eval/eval_set.json"

async def run_evaluation():
    with open(EVAL_SET_PATH, 'r') as f:
        eval_data = json.load(f)

    correct_matches = 0
    total_match_queries = 0
    correct_refusals = 0
    total_refusal_queries = 0

    async with AsyncSessionLocal() as db:
        for item in eval_data:
            # Find the post by title slug (simplified: we'll search by title content)
            post_result = await db.execute(
                select(Post).where(Post.title.ilike(f"%{item['post_slug'].replace('-', ' ')}%"))
            )
            post = post_result.scalar_one_or_none()
            
            if not post:
                print(f"Skipping {item['post_slug']}: Post not found in DB. Did you seed it?")
                continue

            # Get post vector
            pvec_result = await db.execute(select(PostVector).where(PostVector.post_id == post.id))
            pvec = pvec_result.scalar_one_or_none()
            if not pvec:
                print(f"Skipping {item['post_slug']}: No embedding.")
                continue

            # Rank all images
            img_vecs = (await db.execute(select(ImageVector))).scalars().all()
            scored = []
            for ivec in img_vecs:
                sim = cosine_similarity(pvec.embedding, ivec.embedding)
                scored.append({"image_id": ivec.image_id, "similarity": sim})
            scored.sort(key=lambda x: x["similarity"], reverse=True)

            # Run guard on top candidate
            top = scored[0]
            meta = (await db.execute(select(ImageMetadataRecord).where(ImageMetadataRecord.image_id == top["image_id"]))).scalar_one()
            
            decision = evaluate_candidate(post.subject, meta.subject, top["similarity"], meta.confidence)

            if item["expect"] == "match":
                total_match_queries += 1
                # Check if the suggested image matches the expected image ID
                expected_filename = f"{item['expected_image_id']}.jpg"
                expected_img = (await db.execute(select(Image).where(Image.filename == expected_filename))).scalar_one_or_none()
                
                if decision.verdict == "suggest" and expected_img and top["image_id"] == expected_img.id:
                    correct_matches += 1
                    print(f"[PASS] {item['post_slug']}: Matched correctly")
                else:
                    print(f"[FAIL] {item['post_slug']}: Got {decision.verdict} ({meta.subject}) instead of expected {item['expected_image_id']}")

            elif item["expect"] == "no_match":
                total_refusal_queries += 1
                if decision.verdict in ["no_confident_match", "reject"]:
                    correct_refusals += 1
                    print(f"[PASS] {item['post_slug']}: Correctly refused")
                else:
                    print(f"[FAIL] {item['post_slug']}: Should have refused, but got {decision.verdict}")

    # Print Final Score
    print("\n--- EVALUATION RESULTS ---")
    if total_match_queries > 0:
        precision = (correct_matches / total_match_queries) * 100
        print(f"Top-1 Precision: {correct_matches}/{total_match_queries} = {precision:.1f}%")
    if total_refusal_queries > 0:
        print(f"Correct Refusals: {correct_refusals}/{total_refusal_queries}")
    print("--------------------------")
    
    return (correct_matches / total_match_queries * 100) if total_match_queries > 0 else 0.0

if __name__ == "__main__":
    asyncio.run(run_evaluation())