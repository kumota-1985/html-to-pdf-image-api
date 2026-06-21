# Docs タブに貼る内容(英語・Markdown)— HTML to PDF & Image

RapidAPIの **Docs**(About)タブに、下の `---` 内の英語Markdownをそのまま貼ってください。
ロゴは `html_to_pdf_logo.png`(500x500)を General の Upload Logo にアップロード。

---

# HTML to PDF & Image — Documentation

Turn an HTML/CSS template plus JSON data into a **pixel-perfect PDF or PNG/JPEG image** in a single API call. Rendering is done by a real headless Chromium, so full modern CSS, web fonts, flexbox/grid and SVG all work exactly as in a browser.

## How it works

1. You send an **`html_template`** — an HTML string that may contain **Jinja2 placeholders** like `{{ name }}`.
2. You send **`data`** — a JSON object whose keys fill those placeholders.
3. You get back the rendered **PDF** (or **image**) as the binary response body.

```
html_template:  "<h1>Invoice {{ number }}</h1><p>Total: {{ total }}</p>"
data:           { "number": "A-001", "total": "¥10,000" }
   ->  a PDF that reads:  Invoice A-001 / Total: ¥10,000
```

## Authentication

You don't manage any keys yourself. **Subscribe to a plan** (BASIC is free) and use the auto-generated code snippets on the **Endpoints** tab — RapidAPI injects your `X-RapidAPI-Key` / `X-RapidAPI-Host` headers automatically.

## Response format

The response body **is the file** (not JSON):
- `POST /api/generator/pdf` → `Content-Type: application/pdf`
- `POST /api/generator/image` → `Content-Type: image/png` or `image/jpeg`

Save the body to a file, or stream it to your user.

---

## POST /api/generator/pdf

| Field | Type | Required | Notes |
|---|---|---|---|
| `html_template` | string | **yes** | HTML, with optional `{{ }}` Jinja2 placeholders |
| `data` | object | no | values for the placeholders |
| `options` | object | no | see **PDF options** below |

**PDF options**

| Key | Default | Notes |
|---|---|---|
| `format` | `A4` | `A4`, `A3`, `A5`, `Letter`, `Legal` |
| `landscape` | `false` | landscape orientation |
| `printBackground` | `true` | include background colors/images |
| `marginTop` / `marginBottom` / `marginLeft` / `marginRight` | `0px` | CSS units, e.g. `"15mm"`, `"1in"` |

**Example body**
```json
{
  "html_template": "<h1 style='font-family:sans-serif'>Invoice {{ number }}</h1><p>Total: {{ total }}</p>",
  "data": { "number": "A-001", "total": "10,000 JPY" },
  "options": { "format": "A4", "marginTop": "15mm", "marginLeft": "15mm" }
}
```

## POST /api/generator/image

| Field | Type | Required | Notes |
|---|---|---|---|
| `html_template` | string | **yes** | HTML, with optional `{{ }}` placeholders |
| `data` | object | no | values for the placeholders |
| `options` | object | no | see **Image options** below |

**Image options**

| Key | Default | Notes |
|---|---|---|
| `width` | `800` | viewport width in px (1–4000) |
| `height` | `600` | viewport height in px (1–4000) |
| `type` | `png` | `png` or `jpeg` |
| `quality` | — | 1–100, **JPEG only** |

**Example body**
```json
{
  "html_template": "<div style='padding:40px;font:600 36px sans-serif;color:#4F46E5'>Hello {{ name }}</div>",
  "data": { "name": "World" },
  "options": { "type": "png", "width": 1200, "height": 630 }
}
```
(1200×630 is handy for social/OG preview images.)

---

## Templating notes
- Placeholders use **Jinja2** syntax: `{{ value }}`, loops `{% for x in items %}…{% endfor %}`, conditionals `{% if %}`.
- Templates render in a **sandbox** — they can format and arrange your data but cannot run arbitrary server-side code.
- Values are HTML-escaped by default (safe against markup injection from your data).

## External resources (images, CSS, fonts)
- The renderer **can load public `http(s)` resources** referenced in your HTML (e.g. an image URL, a Google Fonts `<link>`).
- For privacy/SSRF safety, requests to **private / internal / loopback / cloud-metadata** addresses are blocked.
- The most reliable approach is to **embed assets as `data:` URIs** so nothing external is fetched.

## Limits
- Viewport up to **4000 × 4000 px**.
- Per-plan request quotas apply (see Pricing). Each call runs a real browser render.

## Disclaimer
Independent service. You are responsible for the content you submit and for having the rights to any assets your templates reference.
