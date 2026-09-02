try:
    from app.config import settings
except ImportError:  # pragma: no cover
    from config import settings

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.database_user,
    password=settings.database_password.get_secret_value(),
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
)

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,          
    pool_pre_ping=True,           
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    """Call on application shutdown."""
    await engine.dispose()