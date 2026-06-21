import ipaddress
from urllib.parse import urlparse

from jinja2.sandbox import SandboxedEnvironment
from playwright.async_api import Browser, Route

from app.core.config import settings
from app.schemas.generator import PDFOptions, ImageOptions

# Sandboxed Jinja2: user-supplied templates can no longer reach Python internals.
# (Plain jinja2.Template(user_input).render() is Server-Side Template Injection -> RCE.)
_jinja_env = SandboxedEnvironment(autoescape=True)


def _block_request(url: str) -> bool:
    """SSRF guard for resources the rendered HTML tries to load.

    Blocks non-http(s) schemes (file:, ftp:, ...) and any host that resolves to a
    private / loopback / link-local / reserved address or a cloud-metadata endpoint.
    Public http(s) hosts are allowed (DNS-rebinding is out of scope for this guard).
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return True
    scheme = (parsed.scheme or "").lower()
    if scheme in ("data", "about", "blob"):
        return False
    if scheme not in ("http", "https"):
        return True
    host = (parsed.hostname or "").lower()
    if not host or host == "localhost" or host.endswith(".localhost") or host == "metadata.google.internal":
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False  # a hostname, not an IP literal -> treat as public
    return (ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_reserved or ip.is_multicast or ip.is_unspecified)


class RendererService:
    @staticmethod
    def render_template(template_str: str, data: dict) -> str:
        """Bind data to an HTML template using a SANDBOXED Jinja2 env (blocks SSTI)."""
        return _jinja_env.from_string(template_str).render(**data)

    @staticmethod
    async def _new_guarded_page(context):
        """A page with request interception (SSRF guard) and a hard default timeout."""
        page = await context.new_page()
        page.set_default_timeout(settings.PLAYWRIGHT_TIMEOUT_MS)

        async def _guard(route: Route):
            if _block_request(route.request.url):
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", _guard)
        return page

    @staticmethod
    async def generate_pdf(browser: Browser, html_content: str, options: PDFOptions) -> bytes:
        """Render HTML to PDF in an isolated, SSRF-guarded, time-bounded context."""
        context = await browser.new_context()
        try:
            page = await RendererService._new_guarded_page(context)
            await page.set_content(html_content, wait_until="networkidle",
                                   timeout=settings.PLAYWRIGHT_TIMEOUT_MS)
            margin = {
                "top": options.margin_top,
                "bottom": options.margin_bottom,
                "left": options.margin_left,
                "right": options.margin_right,
            }
            return await page.pdf(
                format=options.format,
                landscape=options.landscape,
                print_background=options.print_background,
                margin=margin,
            )
        finally:
            await context.close()

    @staticmethod
    async def generate_image(browser: Browser, html_content: str, options: ImageOptions) -> bytes:
        """Render HTML to an image screenshot in an isolated, SSRF-guarded context."""
        context = await browser.new_context(
            viewport={"width": options.width, "height": options.height}
        )
        try:
            page = await RendererService._new_guarded_page(context)
            await page.set_content(html_content, wait_until="networkidle",
                                   timeout=settings.PLAYWRIGHT_TIMEOUT_MS)
            shot_type = "png" if options.type == "png" else "jpeg"
            shot_kwargs = {"type": shot_type, "full_page": False}
            if shot_type == "jpeg" and options.quality is not None:
                shot_kwargs["quality"] = options.quality
            return await page.screenshot(**shot_kwargs)
        finally:
            await context.close()
