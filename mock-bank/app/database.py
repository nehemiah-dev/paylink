from config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = (
        f"postgresql+asyncpg://{settings.database_user}:"
        f"{settings.database_password.get_secret_value()}"
        f"@{settings.database_host}:{settings.database_port}"
        f"/{settings.database_name}")

engine = create_async_engine(url=str(DATABASE_URL))

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal as session:
        yield session