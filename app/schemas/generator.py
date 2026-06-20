from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class PDFOptions(BaseModel):
    format: str = Field("A4", description="用紙サイズ (例: A4, A3, A5, Letter, Legal)")
    landscape: bool = Field(False, description="横向き (True) または 縦向き (False)")
    print_background: bool = Field(True, alias="printBackground", description="背景グラフィックを印刷するかどうか")
    margin_top: str = Field("0px", alias="marginTop", description="上マージン (例: '10px', '1in')")
    margin_bottom: str = Field("0px", alias="marginBottom", description="下マージン")
    margin_left: str = Field("0px", alias="marginLeft", description="左マージン")
    margin_right: str = Field("0px", alias="marginRight", description="右マージン")

    class Config:
        populate_by_name = True  # Pydantic v2: allows using both camelCase and snake_case

class ImageOptions(BaseModel):
    width: int = Field(800, description="ビューポート幅 (px)")
    height: int = Field(600, description="ビューポート高さ (px)")
    type: str = Field("png", description="画像フォーマット ('png' または 'jpeg')")
    quality: Optional[int] = Field(None, description="画質 (jpegの場合のみ有効、1〜100)")

class GeneratePDFRequest(BaseModel):
    html_template: str = Field(..., description="Jinja2プレースホルダー付きのHTMLテンプレート文字列")
    data: Dict[str, Any] = Field(default_factory=dict, description="テンプレート流し込み用データ")
    options: Optional[PDFOptions] = Field(default_factory=PDFOptions, description="PDF印刷オプション")

class GenerateImageRequest(BaseModel):
    html_template: str = Field(..., description="Jinja2プレースホルダー付きのHTMLテンプレート文字列")
    data: Dict[str, Any] = Field(default_factory=dict, description="テンプレート流し込み用データ")
    options: Optional[ImageOptions] = Field(default_factory=ImageOptions, description="画像キャプチャオプション")
