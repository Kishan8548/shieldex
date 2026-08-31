import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.state import load_models, get_app_state
from src.api.routers.predict import router as predict_router
from src.api.routers.metrics_alerts import metrics_router, alerts_router
from src.api.routers.agent_router import router as agent_router
from src.api.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Fraud-Spike Detector API...")
    load_models()
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Shieldex",
    description=(
        "**Razorpay Buildathon — Track 02: AI Risk Manager**\n\n"
        "Two-layer fraud detection system for payment merchants:\n"
        "1. Transaction-level classifier (LightGBM + XGBoost ensemble + SHAP)\n"
        "2. Per-merchant EWMA fraud-rate spike detector\n\n"
        "Defense-only. No offensive or evasion capability."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} [{ms:.1f}ms]")
    response.headers["X-Response-Time-Ms"] = str(round(ms, 1))
    return response


app.include_router(predict_router)
app.include_router(metrics_router)
app.include_router(alerts_router)
app.include_router(agent_router)


@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    state = get_app_state()
    return HealthResponse(
        status="healthy" if state.is_ready else "degraded",
        models_loaded=state.ensemble is not None,
        metrics_loaded=state.test_metrics is not None,
        n_active_alerts=len(state.spike_detector.get_all_active_alerts()) if state.spike_detector else 0,
    )


from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
ASSETS_DIR = DIST_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # Check if a static file in dist exists (e.g. favicon.ico, images)
    target = DIST_DIR / full_path
    if full_path and target.exists() and target.is_file():
        return FileResponse(target)
    
    # Fallback to index.html for React SPA
    index_path = DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    return JSONResponse({
        "service": "Shieldex — Autonomous Payment Risk Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    })

