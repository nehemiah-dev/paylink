from contextlib import asynccontextmanager
from typing import Annotated

from database import Base, dispose_engine, engine, get_db
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        print("Starting database engine...")
        await conn.run_sync(Base.metadata.create_all)
    yield

    print("Shutting down database engine...")
    await dispose_engine()
app = FastAPI(
    lifespan=lifespan,
    title="Mock Bank API",
    version="1.0.0",
    description=("A mock banking API for payment gateway integrations"),
    docs_url="/docs"
)

templates = Jinja2Templates(directory="mock-bank/app/templates")


@app.get("/healthz")
async def health(db: Annotated[AsyncSession, Depends(get_db)]):
    status = {"app": "up"}
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        status["database"] = "up"
    except Exception:  # noqa: BLE001
        status["database"] = "down"
    return status



@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"api_docs_url": app.docs_url})