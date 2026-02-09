# app/db/init_db.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.session import engine
from app.db.base import Base
from app.models.order import Order

async def init_db(engine: AsyncEngine = engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
    print("✅ Tables created successfully")
