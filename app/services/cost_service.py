import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CostLog

logger = logging.getLogger(__name__)

# Gemini Pro Vision free tier rough cost (for tracking pattern, even if $0.00)
COST_PER_IMAGE = 0.0 

async def log_cost(db: AsyncSession, job_id: str, call_type: str, model: str, units: int = 1):
    cost_entry = CostLog(
        job_id=job_id,
        call_type=call_type,
        model=model,
        units=units,
        est_cost_usd=COST_PER_IMAGE
    )
    db.add(cost_entry)
    await db.flush() # Write to DB but keep transaction open for the main image record