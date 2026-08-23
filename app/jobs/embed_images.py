import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import Image, ImageMetadataRecord, ImageVector
from app.services.embedding_service import get_embedding
from app.services.cost_service import log_cost

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-embedding-001"

async def run_image_embedding_job(job_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Image).join(ImageMetadataRecord, Image.id == ImageMetadataRecord.image_id)
            .where(Image.status == "processed")
        )
        images = result.scalars().all()
        
        logger.info(f"Found {len(images)} images to embed.")
        
        for img in images:
            meta_result = await db.execute(
                select(ImageMetadataRecord).where(ImageMetadataRecord.image_id == img.id)
            )
            meta = meta_result.scalar_one()
            
            # Removed 'await' here because get_embedding is no longer async
            embedding = get_embedding(meta.caption)
            
            vec_record = ImageVector(
                image_id=img.id,
                embedding=embedding,
                model=MODEL_NAME
            )
            db.add(vec_record)
            await log_cost(db, job_id=job_id, call_type="embedding", model=MODEL_NAME)
            await db.commit()
            
            await asyncio.sleep(0.5)
            
        logger.info("Image embedding job finished.")