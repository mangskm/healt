import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("health_app")

app = FastAPI(
    title="Personal Health Tracking API",
    version="0.4.0",
    description="Personal health tracking API. It does not provide medical advice.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)
app.include_router(api_router)


@app.middleware("http")
async def request_log(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    logger.info("request completed method=%s path=%s status=%s duration_ms=%.1f", request.method, request.url.path, response.status_code, (time.perf_counter() - started_at) * 1000)
    return response


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, error: Exception) -> JSONResponse:
    logger.error("unhandled request error method=%s path=%s error_type=%s", request.method, request.url.path, type(error).__name__)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
