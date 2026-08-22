import os
from dotenv import load_dotenv

# 1. Load environment variables from .env FIRST
load_dotenv()

import asyncio
from app.db import engine, Base
# Import all models so Base knows about them
from app.models import Image, ImageMetadataRecord, Post, Suggestion, CostLog

async def main():
    # 2. Print the URL to verify it's reading Neon, not localhost
    db_url = os.getenv("DATABASE_URL")
    print(f"Connecting to: {db_url.split('@')[-1]}...") # Hides password in terminal
    
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())