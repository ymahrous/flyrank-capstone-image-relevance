import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import Image, ImageMetadataRecord, ImageVector
from app.services.embedding_service import get_embedding
from app.services.cost_service import log_cost

logger = logging.getLogger(__name__)

async def run_image_embedding_job(job_id: str):
    async with AsyncSessionLocal() as db:
        # Get all processed images that don't have an embedding yet
        result = await db.execute(
            select(Image).join(ImageMetadataRecord, Image.id == ImageMetadataRecord.image_id)
            .where(Image.status == "processed")
        )
        images = result.scalars().all()
        
        logger.info(f"Found {len(images)} images to embed.")
        
        for img in images:
            # Get the caption for this image
            meta_result = await db.execute(
                select(ImageMetadataRecord).where(ImageMetadataRecord.image_id == img.id)
            )
            meta = meta_result.scalar_one()
            
            # Embed the caption
            embedding = await get_embedding(meta.caption)
            
            # Save
            vec_record = ImageVector(
                image_id=img.id,
                embedding=embedding,
                model="text-embedding-004"
            )
            db.add(vec_record)
            await log_cost(db, job_id=job_id, call_type="embedding", model="text-embedding-004")
            await db.commit()
            
            await asyncio.sleep(0.5) # Be polite to API
            
        logger.info("Image embedding job finished.")