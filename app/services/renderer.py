from jinja2 import Template
from playwright.async_api import Browser

from app.schemas.generator import PDFOptions, ImageOptions

class RendererService:
    @staticmethod
    def render_template(template_str: str, data: dict) -> str:
        """Bind dynamic data to an HTML template using Jinja2."""
        template = Template(template_str)
        return template.render(**data)

    @staticmethod
    async def generate_pdf(browser: Browser, html_content: str, options: PDFOptions) -> bytes:
        """
        Render HTML string and generate PDF binary using a shared Playwright browser instance.
        Creates a clean context/page isolated to the request.
        """
        # Create a new browser context and a new page for isolation
        context = await browser.new_context()
        page = await context.new_page()
        try:
            # Set the page content and wait until network connections are idle
            await page.set_content(html_content, wait_until="networkidle")
            
            margin = {
                "top": options.margin_top,
                "bottom": options.margin_bottom,
                "left": options.margin_left,
                "right": options.margin_right
            }
            
            pdf_bytes = await page.pdf(
                format=options.format,
                landscape=options.landscape,
                print_background=options.print_background,
                margin=margin
            )
            return pdf_bytes
        finally:
            # Always close contexts to prevent memory leaks
            await context.close()

    @staticmethod
    async def generate_image(browser: Browser, html_content: str, options: ImageOptions) -> bytes:
        """
        Render HTML string and capture a screenshot using a shared Playwright browser instance.
        """
        # Create a context with the requested viewport size
        context = await browser.new_context(
            viewport={"width": options.width, "height": options.height}
        )
        page = await context.new_page()
        try:
            await page.set_content(html_content, wait_until="networkidle")
            
            shot_type = "png" if options.type == "png" else "jpeg"
            shot_kwargs = {
                "type": shot_type,
                "full_page": False
            }
            # Quality parameter is only valid for JPEG
            if shot_type == "jpeg" and options.quality is not None:
                shot_kwargs["quality"] = options.quality
                
            image_bytes = await page.screenshot(**shot_kwargs)
            return image_bytes
        finally:
            await context.close()
