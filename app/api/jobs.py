import uuid
from fastapi import APIRouter, BackgroundTasks
from app.jobs.process_images import run_vision_batch_job
from app.jobs.embed_images import run_image_embedding_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/vision")
async def start_vision_job(background_tasks: BackgroundTasks):
    job_id = f"vision-{uuid.uuid4().hex[:8]}"
    background_tasks.add_task(run_vision_batch_job, job_id)
    return {"message": "Vision batch job started", "job_id": job_id}

@router.post("/embed-images")
async def start_embed_job(background_tasks: BackgroundTasks):
    job_id = f"embed-{uuid.uuid4().hex[:8]}"
    background_tasks.add_task(run_image_embedding_job, job_id)
    return {"message": "Image embedding job started", "job_id": job_id}