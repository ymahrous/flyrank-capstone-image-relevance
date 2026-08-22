from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.api.posts import router as posts_router
from app.api.matching import router as matching_router

app = FastAPI(title="FlyRank Image Matching Engine")

app.include_router(health_router)
app.include_router(jobs_router)
app.include_router(posts_router)
app.include_router(matching_router)

@app.get("/")
def root():
    return {"message": "FlyRank Capstone API"}