from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="Mock Bank API",
    version="1.0.0",
    description=("A mock banking partner API for payment gateway integrations"),
    docs_url="/docs"
)

templates = Jinja2Templates(directory="mock-bank/app/templates")


@app.get("/healthz")
async def health():
    return {"app": "ok"}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"api_docs_url": app.docs_url})