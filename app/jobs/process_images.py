import os
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import Image, ImageMetadataRecord
from app.services.vision_service import analyze_image
from app.services.cost_service import log_cost

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.70
MODEL_NAME = "gemini-pro-vision"

async def run_vision_batch_job(job_id: str):
    logger.info(f"Starting batch job {job_id}")
    
    async with AsyncSessionLocal() as db:
        # 1. Get all images that are still pending (Idempotency check)
        result = await db.execute(select(Image).where(Image.status == "pending"))
        pending_images = result.scalars().all()
        
        logger.info(f"Found {len(pending_images)} pending images to process.")

        for img_record in pending_images:
            filepath = os.path.join("data/images", img_record.filename)
            
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                img_record.status = "failed"
                await db.flush()
                continue

            # Read image bytes
            with open(filepath, "rb") as f:
                image_bytes = f.read()

            # Retry logic
            max_retries = 3
            metadata = None
            raw_response = ""

            for attempt in range(max_retries):
                try:
                    # Throttle: Free tier limits RPM, sleep to be safe
                    await asyncio.sleep(2) 
                    
                    metadata, raw_response = await analyze_image(image_bytes)
                    
                    if metadata:
                        break # Success
                        
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {img_record.filename}: {e}")
                    await asyncio.sleep(2 ** attempt) # Exponential backoff

            # Log cost regardless of success/failure
            await log_cost(db, job_id=job_id, call_type="vision", model=MODEL_NAME)

            # 4. Handle Result
            if metadata:
                # Low confidence check (The Guard's first line of defense)
                if metadata.confidence < CONFIDENCE_THRESHOLD:
                    img_record.status = "flagged"
                    logger.warning(f"Flagged {img_record.filename} due to low confidence: {metadata.confidence}")
                else:
                    img_record.status = "processed"

                # Save metadata
                meta_db = ImageMetadataRecord(
                    image_id=img_record.id,
                    subject=metadata.subject,
                    category=metadata.category,
                    attributes=metadata.attributes,
                    caption=metadata.caption,
                    confidence=metadata.confidence,
                    model=MODEL_NAME
                )
                db.add(meta_db)
            else:
                img_record.status = "failed"
                logger.error(f"Permanently failed {img_record.filename}. Raw: {raw_response[:100]}")

            # Commit per image so progress is saved if job crashes
            await db.commit()
            
        logger.info(f"Batch job {job_id} finished.")