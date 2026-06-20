import hashlib
from contextlib import asynccontextmanager

# Python 3.8.3 compatibility patch for hashlib.md5
try:
    hashlib.md5(usedforsecurity=False)
except TypeError:
    original_md5 = hashlib.md5
    def md5_patched(*args, **kwargs):
        kwargs.pop('usedforsecurity', None)
        return original_md5(*args, **kwargs)
    hashlib.md5 = md5_patched

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.deps import limiter
from app.routers import r01_generator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Playwright manager and launch a shared headless Chromium browser
    app.state.playwright_mgr = async_playwright()
    playwright = await app.state.playwright_mgr.__aenter__()
    app.state.browser = await playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    )
    yield
    # Shutdown: Close the browser and exit Playwright resource managers
    await app.state.browser.close()
    await app.state.playwright_mgr.__aexit__(None, None, None)

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# Setup SlowAPI Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(r01_generator.router, prefix=settings.API_V1_STR, tags=["Generator"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the HTML to PDF/Image Generator API",
        "docs": f"{settings.API_V1_STR}/docs" if not app.root_path else "/docs"
    }
