import os

from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.review import router as review_router
from app.api.v1.verify import router as verify_router
from app.api.v1.fix import router as fix_router
from app.grounding.router import router as grounding_router


app = FastAPI(title="VeriForge", version="0.1.0")


# API v1 Router
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(review_router)
api_v1_router.include_router(verify_router)
api_v1_router.include_router(fix_router)

app.include_router(api_v1_router)


# Grounding API
app.include_router(
    grounding_router,
    prefix="/ground",
    tags=["grounding"]
)


# Static files mount
static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static"
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home():
    index_path = os.path.join(static_dir, "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path)

    return "<h1>VeriForge Backend Running</h1>"