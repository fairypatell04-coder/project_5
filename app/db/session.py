# For asyncpg + SQLAlchemy
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/orders_db"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
