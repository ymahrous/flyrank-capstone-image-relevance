from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import Suggestion

router = APIRouter(prefix="/suggestions", tags=["suggestions"])

@router.post("/{suggestion_id}/approve")
async def approve_suggestion(suggestion_id: int, db: AsyncSession = Depends(get_db)):
    suggestion = await db.get(Suggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.status = "approved"
    await db.commit()
    return {"message": "Suggestion approved", "suggestion_id": suggestion_id}

@router.post("/{suggestion_id}/reject")
async def reject_suggestion(suggestion_id: int, db: AsyncSession = Depends(get_db)):
    suggestion = await db.get(Suggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.status = "rejected"
    await db.commit()
    return {"message": "Suggestion rejected", "suggestion_id": suggestion_id}