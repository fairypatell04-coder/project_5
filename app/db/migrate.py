# app/db/migrate.py
import asyncio
from sqlalchemy import Index
from sqlalchemy.ext.asyncio import AsyncEngine
from app.db.session import engine
from app.models.order import Order
from app.db.base import Base

async def add_indexes(engine: AsyncEngine = engine):
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
        # Add indexes
        idx1 = Index("idx_order_id", Order.id)
        idx2 = Index("idx_order_product_name", Order.product_name)
        await conn.run_sync(lambda sync_conn: idx1.create(sync_conn))
        await conn.run_sync(lambda sync_conn: idx2.create(sync_conn))

if __name__ == "__main__":
    asyncio.run(add_indexes())
    print("✅ Indexes added successfully")
