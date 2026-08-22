import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.db import engine, Base
# Import ALL models so Base sees the full schema
from app.models import Image, ImageMetadataRecord, Post, Suggestion, CostLog, PostVector, ImageVector

async def migrate():
    async with engine.begin() as conn:
        # Creates ONLY the tables that don't exist yet (post_vectors, image_vectors)
        await conn.run_sync(Base.metadata.create_all)
    print("Migration complete: Vector tables are ready.")

if __name__ == "__main__":
    asyncio.run(migrate())