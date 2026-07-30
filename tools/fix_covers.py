# -*- coding: utf-8 -*-
"""修复：把人文/风景横版占位图/AI视频封面 重做为 900x1350 竖版高清。
不触碰用户自己上传的真照片（dream-tide / mist-forest / valley-dawn / 未标题-3）。
"""
import math
import os
import random

from PIL import Image, ImageDraw

from generate_assets import (vgrad, glow, hills, stars, mist_bands, grass,
                             add_grain, save_jpg, lerp,
                             GOLD, CREAM, GALLERY_DIR)
from generate_more import person, lantern, vine, SIL, SIL2

random.seed(555)

W, H = 900, 1350   # 统一竖版 2:3


# ---------- 人文（竖版街巷） ----------
def humanity_fix():
    out = os.path.join(GALLERY_DIR, "humanity")
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(212)
    for i in range(6):
        size = (W, H)
        stops = [(0.0, (14, 22, 18)), (0.55, (24, 36, 29)), (1.0, (18, 28, 22))]
        img = vgrad(size, stops).convert("RGBA")
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        # 两侧高耸的建筑剪影（竖版构图，向上延伸）
        bw1 = rnd.uniform(200, 300)
        ld.rectangle([0, rnd.uniform(120, 220), bw1, H], fill=SIL2 + (255,))
        ld.rectangle([W - bw1 * 0.9, rnd.uniform(180, 280), W, H], fill=SIL + (255,))
        # 错落暖窗（上下分布更多层）
        for w in range(rnd.randint(6, 9)):
            if rnd.random() < 0.55:
                wx = rnd.uniform(36, bw1 - 56)
            else:
                wx = rnd.uniform(W - bw1 * 0.9 + 28, W - 70)
            wy = rnd.uniform(260, 1000)
            ld.rectangle([wx, wy, wx + 30, wy + 44],
                         fill=(214, 176, 108, rnd.randint(150, 230)))
        img.alpha_composite(layer)
        # 街巷尽头的暖光
        glow(img, (rnd.uniform(330, 570), 1060), 190, GOLD, alpha=55)
        # 路灯（竖版里更高）
        lx = rnd.uniform(360, 540)
        ld2 = ImageDraw.Draw(img)
        ld2.line([(lx, 700), (lx, H)], fill=SIL + (255,), width=9)
        lantern(img, int(lx), 690, r=15)
        # 行人一两个，走向深处
        layer2 = Image.new("RGBA", size, (0, 0, 0, 0))
        l2 = ImageDraw.Draw(layer2)
        for p in range(rnd.randint(1, 2)):
            person(l2, rnd.uniform(300, 600), H - 60, rnd.uniform(220, 300),
                   lean=rnd.uniform(-0.5, 0.5), arm=rnd.choice([None, "hold"]),
                   hat=rnd.choice([None, "wide", "cap"]))
        img.alpha_composite(layer2)
        mist_bands(img, 1000, 1180, alpha=22)
        save_jpg(add_grain(img.convert("RGB"), 4),
                 os.path.join(out, "renwen-%02d.jpg" % (i + 1)), quality=86)
    print("humanity fixed")


# ---------- 风景（竖版，只重做第一版的 5 张横版占位图） ----------
def landscape_fix():
    rnd = random.Random(313)
    # 每张图的竖版构图配方：(天空 stops, 光晕色, 元素)
    recipes = {
        "field-dusk":   dict(stops=[(0.0, (20, 30, 24)), (0.5, (52, 54, 34)), (1.0, (24, 34, 26))],
                             glowc=(206, 158, 92), gy=0.42, kind="field"),
        "golden-wheat": dict(stops=[(0.0, (30, 40, 30)), (0.5, (96, 84, 46)), (1.0, (40, 44, 28))],
                             glowc=(224, 184, 110), gy=0.38, kind="field"),
        "lake-moon":    dict(stops=[(0.0, (10, 16, 14)), (0.55, (20, 32, 28)), (1.0, (14, 22, 18))],
                             glowc=(228, 216, 178), gy=0.30, kind="lake"),
        "night-path":   dict(stops=[(0.0, (9, 14, 12)), (0.6, (16, 26, 21)), (1.0, (12, 18, 15))],
                             glowc=(206, 158, 92), gy=0.62, kind="path"),
        "window-light": dict(stops=[(0.0, (18, 26, 22)), (0.6, (30, 42, 34)), (1.0, (20, 30, 24))],
                             glowc=(214, 176, 108), gy=0.40, kind="window"),
    }
    for name, cfg in recipes.items():
        size = (W, H)
        img = vgrad(size, cfg["stops"]).convert("RGBA")
        gx = rnd.uniform(330, 570)
        gy = int(H * cfg["gy"])
        glow(img, (gx, gy), rnd.uniform(240, 330), cfg["glowc"], alpha=85)
        kind = cfg["kind"]

        if kind == "field":
            # 竖版田野：远处山脊 + 前景麦草
            hills(img, int(H * 0.62), 46, lerp(SIL, cfg["glowc"], 0.10), seed=rnd.randint(1, 99))
            hills(img, int(H * 0.72), 30, SIL, seed=rnd.randint(1, 99))
            grass(img, int(H * 0.86), (64, 62, 36), count=520, seed=rnd.randint(1, 99))
            stars(img, 160, ymax_ratio=0.30, gold_ratio=0.15, seed=rnd.randint(1, 99))
        elif kind == "lake":
            # 湖面：月亮 + 倒影光带 + 水线
            d = ImageDraw.Draw(img)
            d.ellipse([gx - 46, gy - 46, gx + 46, gy + 46], fill=(232, 222, 188, 235))
            wy = int(H * 0.66)
            d.rectangle([0, wy, W, H], fill=(12, 20, 17, 255))
            for k in range(26):   # 碎光倒影
                t = k / 25
                yy = wy + 12 + t * (H - wy - 40)
                ww = 60 * (1 - t * 0.6) * rnd.uniform(0.5, 1.0)
                d.line([(gx - ww, yy), (gx + ww, yy)],
                       fill=(214, 196, 150, int(90 * (1 - t))), width=3)
            hills(img, wy - 16, 22, SIL, seed=rnd.randint(1, 99))
            stars(img, 420, ymax_ratio=0.55, gold_ratio=0.12, seed=rnd.randint(1, 99))
        elif kind == "path":
            # 夜路：蜿蜒小径通向一盏灯
            d = ImageDraw.Draw(img)
            lx = rnd.uniform(380, 520)
            ly = int(H * 0.60)
            lantern(img, int(lx), ly, r=14)
            pts = []
            for k in range(30):
                t = k / 29
                px = lx + (W / 2 - lx) * t + math.sin(t * 5) * 60 * t
                py = ly + (H - ly) * t
                pts.append((px, py))
            d.line(pts, fill=(40, 52, 40, 255), width=26)
            grass(img, int(H * 0.9), (26, 38, 30), count=460, seed=rnd.randint(1, 99))
            stars(img, 500, ymax_ratio=0.5, gold_ratio=0.12, seed=rnd.randint(1, 99))
        elif kind == "window":
            # 窗光：一扇亮窗 + 垂藤 + 桌面剪影
            d = ImageDraw.Draw(img)
            wx0, wy0 = W / 2 - 130, int(H * 0.24)
            d.rectangle([wx0, wy0, wx0 + 260, wy0 + 380], fill=(216, 184, 120, 200))
            d.line([(W / 2, wy0), (W / 2, wy0 + 380)], fill=SIL + (255,), width=8)
            d.line([(wx0, wy0 + 190), (wx0 + 260, wy0 + 190)], fill=SIL + (255,), width=8)
            for v in range(3):
                vine(img, rnd.uniform(80, W - 80), 0, rnd.uniform(200, 420), seed=rnd.randint(1, 99))
            d.rectangle([0, int(H * 0.78), W, H], fill=(16, 24, 19, 255))
            d.polygon([(W/2 - 60, int(H * 0.78)), (W/2 + 60, int(H * 0.78)),
                       (W/2 + 44, int(H * 0.70)), (W/2 - 44, int(H * 0.70))], fill=SIL + (255,))

        save_jpg(add_grain(img.convert("RGB"), 4),
                 os.path.join(GALLERY_DIR, name + ".jpg"), quality=86)
    print("landscape fixed (5 张横版占位图 -> 竖版)")


# ---------- AI 视频封面（竖版高清，只重做两张 640x360 小图） ----------
def video_cover_fix():
    rnd = random.Random(414)
    # 造云机：竖版，云团在塔顶升腾
    size = (W, H)
    img = vgrad(size, [(0.0, (12, 20, 17)), (0.6, (22, 34, 27)), (1.0, (16, 24, 20))]).convert("RGBA")
    glow(img, (W / 2, 420), 300, (150, 170, 150), alpha=60)
    d = ImageDraw.Draw(img)
    # 塔
    d.polygon([(W/2 - 46, H), (W/2 + 46, H), (W/2 + 22, 640), (W/2 - 22, 640)], fill=SIL + (255,))
    d.rectangle([W/2 - 40, 600, W/2 + 40, 650], fill=SIL2 + (255,))
    # 云团（叠三层椭圆 + 模糊感用光晕代替）
    for cx, cy, r in [(W/2, 560, 120), (W/2 - 90, 500, 90), (W/2 + 80, 470, 100), (W/2, 420, 80)]:
        glow(img, (cx, cy), r, (188, 200, 186), alpha=70)
    stars(img, 260, ymax_ratio=0.4, seed=21)
    save_jpg(add_grain(img.convert("RGB"), 4),
             os.path.join(GALLERY_DIR, "cloud-machine.jpg"), quality=86)

    # 萤原：竖版，漂浮光点的原野
    img = vgrad(size, [(0.0, (8, 14, 12)), (0.55, (16, 26, 21)), (1.0, (12, 18, 15))]).convert("RGBA")
    hills(img, int(H * 0.66), 40, SIL2, seed=8)
    hills(img, int(H * 0.76), 26, SIL, seed=9)
    for f in range(46):   # 萤火
        fx = rnd.uniform(40, W - 40)
        fy = rnd.uniform(H * 0.35, H * 0.9)
        glow(img, (fx, fy), rnd.uniform(8, 26), (214, 196, 120), alpha=rnd.randint(60, 130))
    grass(img, int(H * 0.9), (30, 46, 34), count=480, seed=11)
    stars(img, 380, ymax_ratio=0.4, gold_ratio=0.14, seed=22)
    save_jpg(add_grain(img.convert("RGB"), 4),
             os.path.join(GALLERY_DIR, "neon-field.jpg"), quality=86)
    print("video covers fixed")


if __name__ == "__main__":
    humanity_fix()
    landscape_fix()
    video_cover_fix()
    print("ALL FIXED")
