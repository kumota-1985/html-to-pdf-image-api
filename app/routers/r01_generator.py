from fastapi import APIRouter, Request, HTTPException, status, Response

from app.schemas.generator import GeneratePDFRequest, GenerateImageRequest
from app.services.renderer import RendererService
from app.core.deps import limiter
from app.core.config import settings

router = APIRouter()

@router.post("/generator/pdf")
@limiter.limit(settings.RATE_LIMIT_PDF)
async def generate_pdf(request: Request, body: GeneratePDFRequest):
    """
    Generate a PDF from an HTML/CSS template and dynamic data.
    Returns the generated PDF as a binary download.
    """
    try:
        # 1. Populate HTML template with data
        html_content = RendererService.render_template(body.html_template, body.data)
        
        # 2. Access the shared browser instance from app state
        browser = request.app.state.browser
        
        # 3. Render and generate the PDF
        pdf_bytes = await RendererService.generate_pdf(browser, html_content, body.options)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=generated.pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )

@router.post("/generator/image")
@limiter.limit(settings.RATE_LIMIT_IMAGE)
async def generate_image(request: Request, body: GenerateImageRequest):
    """
    Generate an image (PNG/JPEG) from an HTML/CSS template and dynamic data.
    Returns the raw image payload.
    """
    try:
        # 1. Populate HTML template with data
        html_content = RendererService.render_template(body.html_template, body.data)
        
        # 2. Access the shared browser instance from app state
        browser = request.app.state.browser
        
        # 3. Render and capture the image screenshot
        image_bytes = await RendererService.generate_image(browser, html_content, body.options)
        
        media_type = "image/png" if body.options.type == "png" else "image/jpeg"
        ext = "png" if body.options.type == "png" else "jpg"
        
        return Response(
            content=image_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename=capture.{ext}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}"
        )
