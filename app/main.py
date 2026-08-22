from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router

app = FastAPI(title="FlyRank Image Matching Engine")

app.include_router(health_router, tags=["health"])
app.include_router(jobs_router)

@app.get("/")
def root():
    return {"message": "FlyRank Capstone API"}