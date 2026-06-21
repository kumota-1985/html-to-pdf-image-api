#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML to PDF & Image Generator のマーケット用ロゴ(500x500 PNG)を生成。
コンセプト: コード(</>) から書類(テキスト行) と 画像 を生成する = HTML→PDF/画像。"""
import os
from PIL import Image, ImageDraw

W = 500
INDIGO = (79, 70, 229, 255)     # #4F46E5 背景
WHITE = (255, 255, 255, 255)
PAPER = (248, 250, 252, 255)    # ほぼ白の紙面
AMBER = (245, 158, 11, 255)     # アクセント(画像枠・差し色)
GRAY = (148, 163, 184, 255)     # テキスト行
INK = INDIGO                    # コードグリフ

img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 角丸インディゴ背景
d.rounded_rectangle([0, 0, W - 1, W - 1], radius=112, fill=INDIGO)

# 白い書類(ページ)
px0, py0, px1, py1 = 142, 92, 358, 408
d.rounded_rectangle([px0, py0, px1, py1], radius=26, fill=PAPER)

# 上部: </> コードグリフ(HTML/コード入力の象徴)
cy = 158
d.line([(232, 136), (206, cy), (232, 180)], fill=INK, width=12, joint="curve")   # <
d.line([(247, 184), (263, 132)], fill=INK, width=12)                              # /
d.line([(278, 136), (304, cy), (278, 180)], fill=INK, width=12, joint="curve")   # >

# 中部: テキスト行3本(生成された文書)
for i, (x_end) in enumerate([326, 326, 286]):
    y = 224 + i * 30
    d.rounded_rectangle([176, y - 7, x_end, y + 7], radius=7, fill=GRAY)

# 下部: 画像プレースホルダ(PDFだけでなく画像出力もできる象徴)
bx0, by0, bx1, by1 = 176, 312, 324, 380
d.rounded_rectangle([bx0, by0, bx1, by1], radius=12, outline=AMBER, width=9)
d.ellipse([196, 326, 218, 348], fill=AMBER)                                       # 太陽
d.polygon([(186, 372), (214, 342), (242, 372)], fill=AMBER)                       # 山1
d.polygon([(230, 372), (258, 350), (300, 372)], fill=AMBER)                       # 山2
d.rectangle([bx0 + 9, by1 - 9, bx1 - 9, by1 - 1], fill=PAPER)                     # 枠下を紙色で整える

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_to_pdf_logo.png")
img.save(out)
print("saved:", out, img.size)
