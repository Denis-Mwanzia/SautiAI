"""
FastAPI Application Entry Point
Main application configuration and middleware setup
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import logging
import uuid
import time

from app.core.config import settings
from app.api.v1 import api_router
from app.db.supabase import init_supabase

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Sauti AI Backend...")
    await init_supabase()
    logger.info("Supabase initialized")
    # Optional Sentry
    try:
        if settings.SENTRY_DSN:
            import sentry_sdk
            sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)
            logger.info("Sentry initialized")
    except Exception as e:
        logger.warning(f"Sentry init skipped: {e}")
    yield
    # Shutdown
    logger.info("Shutting down Sauti AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="Sauti AI API",
    description="Voice of the People - Civic Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
)

# GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse({
        "message": "Sauti AI - Voice of the People API",
        "version": "1.0.0",
        "status": "operational"
    })


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "sauti-ai-backend"
    })


@app.middleware("http")
async def add_security_headers_and_request_id(request: Request, call_next):
    """Add security headers and request ID for tracing"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    # Build CSP with allowed frontend and connect-src
    try:
      fe_origins = settings.FRONTEND_ORIGINS if isinstance(settings.FRONTEND_ORIGINS, list) else [o.strip() for o in str(settings.FRONTEND_ORIGINS).split(',') if o.strip()]
      connect_extra = settings.CONNECT_SRC_EXTRA if isinstance(settings.CONNECT_SRC_EXTRA, list) else [o.strip() for o in str(settings.CONNECT_SRC_EXTRA).split(',') if o.strip()]
      backend_http = (settings.PUBLIC_BACKEND_ORIGIN or '').strip() or 'http://localhost:8000'
      backend_ws = backend_http.replace('https', 'wss').replace('http', 'ws')
      connect_src = ['\'self\'', backend_http, backend_ws, 'ws:', 'wss:'] + fe_origins + connect_extra
      csp = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; "
        f"connect-src {' '.join(connect_src)}"
      )
      response.headers["Content-Security-Policy"] = csp
    except Exception:
      # Fallback minimal CSP
      response.headers["Content-Security-Policy"] = (
          "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'"
      )
    return response


@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    """Add HTTP cache headers for GET requests"""
    response = await call_next(request)
    
    if request.method == "GET":
        path = str(request.url.path)
        
        # Dashboard and transparency data: cache for 1 minute
        if "/dashboard" in path or "/transparency" in path:
            response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=30"
        # Real-time data: no cache
        elif "/realtime" in path or "/alerts" in path:
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
        # Default: short cache
        else:
            response.headers["Cache-Control"] = "public, max-age=30"
    
    return response


@app.middleware("http")
async def add_performance_monitoring(request: Request, call_next):
    """Monitor request performance and log slow requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log slow requests (> 1 second)
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    # Add performance header
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    return response


@app.middleware("http")
async def add_etag_caching(request: Request, call_next):
    """Add weak ETag for cacheable GET responses; respect If-None-Match"""
    if request.method != "GET":
        return await call_next(request)
    response = await call_next(request)
    try:
        # Skip ETag for large responses (> 1MB) to avoid memory issues
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:
            return response
        
        # Only for JSON responses
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        # Reconstruct the response body iterator for downstream
        async def new_body_iter():
            yield body
        response.body_iterator = new_body_iter()
        import hashlib
        etag = 'W/"' + hashlib.sha1(body).hexdigest() + '"'
        inm = request.headers.get("If-None-Match")
        response.headers["ETag"] = etag
        if inm and inm == etag:
            # Not modified
            from starlette.responses import Response
            return Response(status_code=304)
    except Exception:
        return response
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )

