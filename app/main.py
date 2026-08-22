from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(title="FlyRank Image Matching Engine")

app.include_router(health_router, tags=["health"])

@app.get("/")
def root():
    return {"message": "FlyRank Capstone API"}