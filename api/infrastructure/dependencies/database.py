"""Database dependencies."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# This is a placeholder - in a real application, you would get these from environment variables
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@postgres/geih_dev"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session():
    """Get database session dependency."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
