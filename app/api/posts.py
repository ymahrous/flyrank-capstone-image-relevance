from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db import get_db
from app.models import Post, PostVector
from app.services.post_service import extract_post_metadata
from app.services.embedding_service import get_embedding
from app.services.cost_service import log_cost

router = APIRouter(prefix="/posts", tags=["posts"])

class PostCreate(BaseModel):
    title: str
    content: str

@router.post("/")
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    metadata = await extract_post_metadata(post.content)
    
    new_post = Post(
        title=post.title,
        content=post.content,
        subject=metadata.subject,
        category=metadata.category
    )
    db.add(new_post)
    await db.flush()
    
    text_to_embed = f"{post.title} {post.content}"
    
    # Removed 'await' here because get_embedding is no longer async
    embedding = get_embedding(text_to_embed)
    
    vec_record = PostVector(
        post_id=new_post.id,
        embedding=embedding,
        model="gemini-embedding-001"
    )
    db.add(vec_record)
    
    await log_cost(db, job_id=f"post-{new_post.id}", call_type="embedding", model="gemini-embedding-001")
    
    await db.commit()
    return {"id": new_post.id, "subject": metadata.subject, "status": "created"}