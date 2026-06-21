from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.core.database import init_db
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="FB Ad Library Automation",
    description="Ricerca inserzioni FB, analizza con Claude, invia messaggi mirati.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_file = Path("templates/index.html")
    if html_file.exists():
        return html_file.read_text()
    return "<h1>FB Automation API</h1><p><a href='/docs'>Swagger Docs</a></p>"
