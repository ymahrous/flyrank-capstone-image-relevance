import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks
from app.jobs.process_images import run_vision_batch_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/vision")
async def start_vision_job(background_tasks: BackgroundTasks):
    job_id = f"vision-{uuid.uuid4().hex[:8]}"
    # Run in the background so it doesn't block the HTTP request
    background_tasks.add_task(run_vision_batch_job, job_id)
    return {"message": "Vision batch job started", "job_id": job_id}