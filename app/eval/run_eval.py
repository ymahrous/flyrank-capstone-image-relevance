import os
import json
import asyncio
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import Post, PostVector, ImageVector, Image, ImageMetadataRecord
from app.services.embedding_service import get_embedding, cosine_similarity
from app.services.guard_service import evaluate_candidate
from app.services.post_service import extract_post_metadata

EVAL_SET_PATH = "app/eval/eval_set.json"

async def ensure_post_exists(db: AsyncSession, title: str, content: str) -> int:
    """Finds a post by title, or creates it + its embedding if it doesn't exist."""
    result = await db.execute(select(Post).where(Post.title.ilike(f"%{title}%")))
    post = result.scalar_one_or_none()
    
    if post:
        return post.id
        
    # Post doesn't exist, create it automatically
    print(f"  -> Auto-creating missing post: {title}")
    metadata = await extract_post_metadata(content)
    
    new_post = Post(
        title=title,
        content=content,
        subject=metadata.subject,
        category=metadata.category
    )
    db.add(new_post)
    await db.flush()
    
    # Generate and save embedding
    text_to_embed = f"{title} {content}"
    embedding = await get_embedding(text_to_embed)
    
    vec_record = PostVector(
        post_id=new_post.id,
        embedding=embedding,
        model="gemini-embedding-001"
    )
    db.add(vec_record)
    await db.commit()
    return new_post.id

async def run_evaluation():
    with open(EVAL_SET_PATH, 'r') as f:
        eval_data = json.load(f)

    # Mock content for auto-creation based on slugs
    slug_to_content = {
        "red-fox-behavior": "Red foxes are solitary hunters that primarily feed on rodents and rabbits.",
        "arctic-fox-habitat": "The arctic fox is incredibly well adapted to the cold, living in some of the most frigid extremes on Earth.",
        "wolf-pack-dynamics": "Gray wolves live in complex social packs led by an alpha pair.",
        "gray-wolf-conservation": "Conservation efforts have helped restore gray wolf populations in certain areas.",
        "labrador-retriever-care": "Labrador retrievers are friendly, outgoing, and high-spirited companions who have more than enough affection to go around.",
        "grizzly-bear-facts": "Grizzly bears are powerful, top-of-the-food-chain predators.",
        "white-tailed-deer-diet": "White-tailed deer are herbivores, leisurely grazing on most available plant foods.",
        "quantum-computing-basics": "Quantum computing uses qubits to perform calculations at speeds unimaginable with classical silicon processors.",
        "history-of-the-roman-empire": "The Roman Empire was one of the largest empires in the ancient world."
    }

    correct_matches = 0
    total_match_queries = 0
    correct_refusals = 0
    total_refusal_queries = 0

    async with AsyncSessionLocal() as db:
        # Get all image vectors once for efficiency
        img_vecs = (await db.execute(select(ImageVector))).scalars().all()
        
        if not img_vecs:
            print("ERROR: No image vectors found. Please run the /jobs/embed-images endpoint first.")
            return 0.0

        for item in eval_data:
            slug = item['post_slug']
            title = slug.replace('-', ' ').title()
            content = slug_to_content.get(slug, f"Blog post about {title}.")
            
            print(f"Evaluating: {title}...")
            
            # 1. Ensure post exists in DB (creates it if not)
            post_id = await ensure_post_exists(db, title, content)
            
            # 2. Get post vector
            pvec_result = await db.execute(select(PostVector).where(PostVector.post_id == post_id))
            pvec = pvec_result.scalar_one_or_none()
            if not pvec:
                print(f"  -> [FAIL] Failed to generate embedding.")
                continue

            # 3. Rank images
            scored = []
            for ivec in img_vecs:
                sim = cosine_similarity(pvec.embedding, ivec.embedding)
                scored.append({"image_id": ivec.image_id, "similarity": sim})
            scored.sort(key=lambda x: x["similarity"], reverse=True)

            # 4. Run guard on top candidate
            top = scored[0]
            meta = (await db.execute(select(ImageMetadataRecord).where(ImageMetadataRecord.image_id == top["image_id"]))).scalar_one()
            
            decision = evaluate_candidate(post.subject, meta.subject, top["similarity"], meta.confidence)

            # 5. Evaluate result
            if item["expect"] == "match":
                total_match_queries += 1
                expected_filename = f"{item['expected_image_id']}.jpg"
                expected_img = (await db.execute(select(Image).where(Image.filename == expected_filename))).scalar_one_or_none()
                
                if decision.verdict == "suggest" and expected_img and top["image_id"] == expected_img.id:
                    correct_matches += 1
                    print(f"  -> [PASS] Matched correctly ({meta.subject})")
                else:
                    print(f"  -> [FAIL] Got {decision.verdict} ({meta.subject}) instead of {item['expected_image_id']}")

            elif item["expect"] == "no_match":
                total_refusal_queries += 1
                if decision.verdict in ["no_confident_match", "reject"]:
                    correct_refusals += 1
                    print(f"  -> [PASS] Correctly refused")
                else:
                    print(f"  -> [FAIL] Should have refused, but got {decision.verdict} ({meta.subject})")

    # Print Final Score
    print("\n--- EVALUATION RESULTS ---")
    if total_match_queries > 0:
        precision = (correct_matches / total_match_queries) * 100
        print(f"Top-1 Precision: {correct_matches}/{total_match_queries} = {precision:.1f}%")
    else:
        print("Top-1 Precision: N/A (No match queries evaluated)")
        
    if total_refusal_queries > 0:
        print(f"Correct Refusals: {correct_refusals}/{total_refusal_queries}")
    print("--------------------------")
    
    return (correct_matches / total_match_queries * 100) if total_match_queries > 0 else 0.0

if __name__ == "__main__":
    asyncio.run(run_evaluation())