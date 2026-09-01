from contextlib import asynccontextmanager

from database import Base, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        print("Starting database engine...")
        await conn.run_sync(Base.metadata.create_all)
    yield

    print("Shutting down database engine...")
    engine.dispose()

app = FastAPI(
    lifespan=lifespan,
    title="Mock Bank API",
    version="1.0.0",
    description=("A mock banking API for payment gateway integrations"),
    docs_url="/docs"
)

templates = Jinja2Templates(directory="mock-bank/app/templates")


@app.get("/healthz")
async def health():
    return {"app": "ok"}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"api_docs_url": app.docs_url})