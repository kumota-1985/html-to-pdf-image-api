# HTML to PDF/Image Generator API

## 🎯 概要
本プロジェクトは、HTML/CSSテンプレートと動的なJSONデータ（Jinja2対応）を受け取り、ヘッドレスブラウザ（Playwright）を用いて高品質なPDFドキュメントや高解像度画像を生成するREST APIです。

AIエージェントや外部自動化ツール（Zapier / Make など）から呼び出され、請求書の自動生成、レポートPDFの出力、ブログやSNSのOGP画像の動的生成などを低遅延で実現することを目的としています。

## 🚀 特徴
- **ブラウザ・プーリング**: リクエストごとにブラウザを起動するのではなく、FastAPIの `lifespan` 内で一度だけChromiumブラウザを起動して共有（プール）します。リクエスト時は一時的なコンテキストとページのみを作成・破棄するため、起動オーバーヘッドを極限まで削減し、高速（低遅延）に動作します。
- **Jinja2内蔵**: HTMLテンプレート内に `{{ variable }}` を含めることで、動的なデータの埋め込みと条件分岐やループ処理に対応。
- **レートリミット**: 各エンドポイントに SlowAPI を用いたアクセス制限（IPベース）を適用。

## 📂 ディレクトリ構成
```text
html-to-pdf-image-api/
├── app/
│   ├── main.py                     # アプリ起動、Lifespan（Playwright共有）、CORS、ルーター結合
│   ├── core/
│   │   ├── config.py               # グローバル設定
│   │   └── deps.py                 # SlowAPIリミッター
│   ├── schemas/
│   │   └── generator.py            # PDF/画像リクエスト・レスポンススキーマ
│   ├── services/
│   │   └── renderer.py             # Jinja2バインド ＆ Playwrightレンダリングロジック
│   └── routers/
│       └── r01_generator.py        # 生成APIエンドポイント (POST /generator/pdf, POST /generator/image)
├── tests/
│   ├── conftest.py             # TestClientフィクスチャ
│   └── test_endpoints.py       # pytest自動テスト
├── requirements.txt            # 依存関係
└── .gitignore
```

## 🛠️ セットアップ手順

### 1. 仮想環境の構築と依存モジュールのインストール
```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 依存モジュールのインストール
pip install -r requirements.txt
```

### 2. Playwright Chromiumのインストール
APIが内部で使用するブラウザバイナリをセットアップします。
```bash
.\venv\Scripts\playwright install chromium
```

### 3. サーバーの起動
```bash
.\venv\Scripts\uvicorn app.main:app --reload
```
起動後、[http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs) にアクセスするとSwagger UIでAPIのテストが可能です。

## 🧪 テストの実行
`pytest` を用いて、実際のPlaywrightの呼び出しとPDF/PNGバイナリ署名の検証テストを実行します。
```bash
.\venv\Scripts\python -m pytest
```
