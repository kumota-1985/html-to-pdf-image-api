def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_generate_pdf_success(client):
    # Prepare HTML template with Jinja2 placeholders and basic CSS styling
    html_template = """
    <html>
      <head>
        <style>
          body { font-family: sans-serif; color: #333; }
          h1 { color: #0066cc; }
        </style>
      </head>
      <body>
        <h1>Invoice Summary</h1>
        <p>Dear {{ name }},</p>
        <p>Your invoice total for this month is: <strong>${{ total }}</strong></p>
      </body>
    </html>
    """
    
    response = client.post(
        "/api/generator/pdf",
        json={
            "html_template": html_template,
            "data": {"name": "Alice Developer", "total": "2,490.50"},
            "options": {
                "format": "A4",
                "landscape": False,
                "printBackground": True
            }
        }
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # Assert PDF file signature (%PDF-)
    content = response.content
    assert len(content) > 0
    assert content.startswith(b"%PDF-")

def test_generate_image_success(client):
    html_template = """
    <html>
      <body style="margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; color: white; font-family: sans-serif;">
        <h1 style="font-size: 48px;">{{ title }}</h1>
      </body>
    </html>
    """
    
    response = client.post(
        "/api/generator/image",
        json={
            "html_template": html_template,
            "data": {"title": "FastAPI Webhook OGP Image Generator"},
            "options": {
                "width": 1200,
                "height": 630,
                "type": "png"
            }
        }
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    # Assert PNG file signature (\x89PNG\r\n\x1a\n)
    content = response.content
    assert len(content) > 0
    assert content.startswith(b"\x89PNG\r\n\x1a\n")
