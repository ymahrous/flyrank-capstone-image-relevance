import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from app.db import engine

# Tables to wipe, in order of dependencies
TABLES_TO_WIPE = [
    "suggestions",
    "post_vectors",
    "image_vectors",
    "cost_log",
    "image_metadata",
    "images",
    "posts"
]

async def reset():
    async with engine.begin() as conn:
        for table in TABLES_TO_WIPE:
            await conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
        print("Database wiped clean.")
    
    # Re-seed the 50 images
    from app.models import Image
    import json
    from app.db import AsyncSessionLocal
    
    with open("data/manifest.json", "r") as f:
        manifest = json.load(f)

    async with AsyncSessionLocal() as db:
        for item in manifest:
            new_img = Image(
                filename=f"{item['id']}.jpg",
                source_url=item["url"],
                license_info="Unsplash License"
            )
            db.add(new_img)
        await db.commit()
        print(f"Re-seeded {len(manifest)} image records.")

if __name__ == "__main__":
    asyncio.run(reset())