import os
import json
import asyncio
from dotenv import load_dotenv

# MUST load .env before importing app.db
load_dotenv()

from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import Image

async def seed():
    # Quick fail-safe check
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL is missing! Check your .env file.")

    with open("data/manifest.json", "r") as f:
        manifest = json.load(f)

    async with AsyncSessionLocal() as db:
        for item in manifest:
            # Check if already seeded (idempotency)
            existing = await db.execute(
                Image.__table__.select().where(Image.filename == f"{item['id']}.jpg")
            )
            if existing.first():
                continue

            new_img = Image(
                filename=f"{item['id']}.jpg",
                source_url=item["url"],
                license_info="Unsplash License"
            )
            db.add(new_img)
        
        await db.commit()
        print(f"Seeded {len(manifest)} image records.")

if __name__ == "__main__":
    asyncio.run(seed())