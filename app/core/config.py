import os

from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "HTML to PDF/Image Generator API"
    API_V1_STR: str = "/api"

    # When set, lock the origin to RapidAPI-proxied traffic (empty = open, for local/dev).
    RAPIDAPI_PROXY_SECRET: str = os.environ.get("RAPIDAPI_PROXY_SECRET", "")
    
    # Rate Limiting
    RATE_LIMIT_PDF: str = "10/minute"
    RATE_LIMIT_IMAGE: str = "10/minute"
    
    # Playwright Settings
    PLAYWRIGHT_TIMEOUT_MS: int = 30000  # 30 seconds

settings = Settings()
