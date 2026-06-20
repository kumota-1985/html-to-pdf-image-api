from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "HTML to PDF/Image Generator API"
    API_V1_STR: str = "/api"
    
    # Rate Limiting
    RATE_LIMIT_PDF: str = "10/minute"
    RATE_LIMIT_IMAGE: str = "10/minute"
    
    # Playwright Settings
    PLAYWRIGHT_TIMEOUT_MS: int = 30000  # 30 seconds

settings = Settings()
