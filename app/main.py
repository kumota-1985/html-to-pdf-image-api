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

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from playwright.async_api import async_playwright
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.deps import limiter, require_proxy_secret
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
    allow_credentials=False,   # public API uses header keys, not cookies; "*"+credentials is invalid
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers (gated by the RapidAPI proxy secret when configured)
app.include_router(r01_generator.router, prefix=settings.API_V1_STR, tags=["Generator"],
                   dependencies=[Depends(require_proxy_secret)])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the HTML to PDF/Image Generator API",
        "docs": f"{settings.API_V1_STR}/docs" if not app.root_path else "/docs"
    }


@app.get("/llms.txt", response_class=PlainTextResponse, include_in_schema=False)
def llms_txt():
    """AIエージェント/検索AI 向けの自己紹介(自動発見・推薦の導線)。認証不要で読める。"""
    return """# HTML to PDF & Image Generator API
> Render an HTML/CSS + JSON-data template into a pixel-perfect PDF or PNG/JPEG image in one call.

Base URL: https://html-to-pdf-image-api.onrender.com
Docs: https://html-to-pdf-image-api.onrender.com/docs
OpenAPI: https://html-to-pdf-image-api.onrender.com/openapi.json

## Endpoints
- POST /api/generator/pdf - HTML template + data -> PDF (format/margins/landscape options)
- POST /api/generator/image - HTML template + data -> PNG/JPEG (viewport width/height, max 4000)
- Templating: Jinja2 placeholders ({{ var }}), rendered in a sandbox; full modern CSS via headless Chromium
- Access: via the RapidAPI marketplace (subscribe for a key)
"""
