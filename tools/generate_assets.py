# -*- coding: utf-8 -*-
"""
为摄影师个人网站生成占位视觉素材：
- 深绿低饱和 + 暖金点缀 的氛围感占位图（山丘/雾气/星野/麦田等）
- 3 段 AI 视频占位短片（缓慢流动的雾与光点）及海报帧
所有素材均为本地生成，无外部依赖，可直接部署 GitHub Pages。
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

random.seed(42)
np.random.seed(42)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets", "img")
GALLERY_DIR = os.path.join(IMG_DIR, "gallery")
VIDEO_DIR = os.path.join(ROOT, "assets", "videos")
os.makedirs(GALLERY_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# ---- 调色板（深绿低饱和 + 暖金）----
DEEP = (18, 28, 22)        # 最深的绿黑
PINE = (27, 40, 31)        # 松绿
MOSS = (44, 62, 50)        # 苔绿
SAGE = (94, 116, 99)       # 灰绿
MIST = (150, 166, 148)     # 雾色
GOLD = (200, 169, 107)     # 暖金
CREAM = (232, 228, 214)    # 米白
NIGHT = (13, 20, 18)       # 夜空


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, stops):
    """垂直渐变，stops: [(pos0-1, color), ...]"""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                local = (t - p0) / max(p1 - p0, 1e-6)
                px[0, y] = lerp(c0, c1, local)
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((w, h))


def add_grain(img, strength=10):
    arr = np.asarray(img).astype(np.int16)
    noise = np.random.normal(0, strength, arr.shape[:2])[..., None]
    out = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def glow(draw_img, center, radius, color, alpha=120):
    """柔和光晕"""
    overlay = Image.new("RGBA", draw_img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cx, cy = center
    steps = 24
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(alpha * (1 - i / steps) ** 1.6)
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius / 6))
    draw_img.alpha_composite(overlay)


def hills(img, base_y, amp, color, seed=0, blur=0):
    """画一层山丘剪影"""
    rnd = random.Random(seed)
    w, h = img.size
    pts = []
    x = -50
    phase = rnd.uniform(0, 6.28)
    f1 = rnd.uniform(0.002, 0.004)
    f2 = rnd.uniform(0.006, 0.012)
    while x < w + 50:
        y = base_y + amp * math.sin(x * f1 + phase) + amp * 0.4 * math.sin(x * f2 + phase * 2)
        pts.append((x, y))
        x += 8
    poly = pts + [(w + 50, h + 50), (-50, h + 50)]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.polygon(poly, fill=color + (255,))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def mist_bands(img, y0, y1, alpha=36):
    w, h = img.size
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    rnd = random.Random(7)
    y = y0
    while y < y1:
        hh = rnd.randint(14, 42)
        bd.ellipse([-w * 0.2, y, w * 1.2, y + hh], fill=MIST + (alpha,))
        y += hh * 1.4
    band = band.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(band)


def stars(img, count, ymax_ratio=1.0, gold_ratio=0.12, seed=1):
    rnd = random.Random(seed)
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for _ in range(count):
        x = rnd.uniform(0, w)
        y = rnd.uniform(0, h * ymax_ratio)
        r = rnd.uniform(0.4, 1.6)
        big = rnd.random() < 0.06
        if big:
            r = rnd.uniform(1.6, 2.4)
        col = GOLD if rnd.random() < gold_ratio else CREAM
        a = rnd.randint(90, 220)
        ld.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
        if big:
            ld.line([x - r * 4, y, x + r * 4, y], fill=col + (a // 3,), width=1)
            ld.line([x, y - r * 4, x, y + r * 4], fill=col + (a // 3,), width=1)
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    img.alpha_composite(layer)


def grass(img, y0, color, count=500, seed=3):
    rnd = random.Random(seed)
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for _ in range(count):
        x = rnd.uniform(0, w)
        y = rnd.uniform(y0, h)
        ln = rnd.uniform(10, 42) * (y - y0) / max(h - y0, 1) + 6
        tilt = rnd.uniform(-6, 6)
        a = rnd.randint(60, 150)
        ld.line([x, y, x + tilt, y - ln], fill=color + (a,), width=1)
    img.alpha_composite(layer)


def save_jpg(img, path, quality=86):
    img.convert("RGB").save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    print("saved:", os.path.relpath(path, ROOT))


def base_rgba(size):
    return Image.new("RGBA", size, (0, 0, 0, 255))


# ---------- 1. 首屏星空背景 ----------
def hero_nebula():
    size = (1920, 1080)
    img = vgrad(size, [(0.0, (10, 16, 14)), (0.55, NIGHT), (1.0, (20, 30, 24))]).convert("RGBA")
    # 星云：几大团柔和绿金色雾
    neb = Image.new("RGBA", size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(neb)
    rnd = random.Random(11)
    for _ in range(9):
        cx = rnd.uniform(0, 1920)
        cy = rnd.uniform(0, 700)
        rx = rnd.uniform(180, 460)
        ry = rx * rnd.uniform(0.3, 0.6)
        col = MOSS if rnd.random() < 0.6 else (58, 66, 44)
        nd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col + (26,))
    neb = neb.filter(ImageFilter.GaussianBlur(90))
    img.alpha_composite(neb)
    glow(img, (1520, 240), 260, GOLD, alpha=40)   # 右上角一点暖金光
    stars(img, 900, ymax_ratio=0.95, seed=5)
    img = add_grain(img.convert("RGB"), 6)
    save_jpg(img, os.path.join(IMG_DIR, "hero-nebula.jpg"), quality=84)


# ---------- 2. 摄影占位图 ----------
def photo_field_dusk():
    size = (1200, 800)
    img = vgrad(size, [(0.0, (52, 66, 52)), (0.45, (86, 96, 66)), (0.62, (140, 128, 84)), (1.0, (30, 42, 33))]).convert("RGBA")
    glow(img, (860, 400), 300, GOLD, alpha=130)
    hills(img, 520, 60, lerp(PINE, GOLD, 0.15), seed=21)
    hills(img, 590, 46, PINE, seed=22)
    hills(img, 670, 30, DEEP, seed=23)
    grass(img, 640, (70, 88, 66), count=700)
    mist_bands(img, 470, 560, alpha=26)
    save_jpg(add_grain(img.convert("RGB"), 8), os.path.join(GALLERY_DIR, "field-dusk.jpg"))


def photo_mist_forest():
    size = (800, 1200)
    img = vgrad(size, [(0.0, (96, 112, 96)), (0.5, (58, 76, 60)), (1.0, (22, 33, 26))]).convert("RGBA")
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    rnd = random.Random(31)
    # 远景树干
    for depth in range(3):
        alpha = [40, 80, 150][depth]
        col = [(70, 86, 72), (44, 60, 48), (24, 35, 28)][depth]
        for _ in range(10 - depth * 2):
            x = rnd.uniform(0, 800)
            wdt = rnd.uniform(4, 10) + depth * 3
            ld.rectangle([x, 80 + depth * 100, x + wdt, 1200], fill=col + (alpha,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(2)))
    mist_bands(img, 300, 900, alpha=42)
    grass(img, 1000, (52, 68, 54), count=400)
    save_jpg(add_grain(img.convert("RGB"), 8), os.path.join(GALLERY_DIR, "mist-forest.jpg"))


def photo_golden_wheat():
    size = (1200, 800)
    img = vgrad(size, [(0.0, (120, 110, 70)), (0.5, (168, 146, 88)), (0.75, (150, 124, 70)), (1.0, (74, 66, 42))]).convert("RGBA")
    glow(img, (300, 260), 320, (232, 200, 130), alpha=120)
    rnd = random.Random(41)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for _ in range(1500):
        x = rnd.uniform(0, 1200)
        y = rnd.uniform(430, 800)
        ln = rnd.uniform(14, 60) * (y - 400) / 400 + 8
        tilt = rnd.uniform(-8, 8)
        shade = rnd.random()
        col = lerp((120, 100, 56), (222, 190, 118), shade)
        a = rnd.randint(90, 200)
        ld.line([x, y, x + tilt, y - ln], fill=col + (a,), width=1)
    img.alpha_composite(layer)
    mist_bands(img, 380, 470, alpha=24)
    save_jpg(add_grain(img.convert("RGB"), 8), os.path.join(GALLERY_DIR, "golden-wheat.jpg"))


def photo_lake_moon():
    size = (1200, 800)
    img = vgrad(size, [(0.0, (12, 20, 18)), (0.5, (22, 34, 28)), (0.62, (30, 44, 36)), (1.0, (14, 22, 19))]).convert("RGBA")
    stars(img, 420, ymax_ratio=0.5, seed=51)
    glow(img, (600, 210), 130, CREAM, alpha=170)
    d = ImageDraw.Draw(img)
    d.ellipse([566, 176, 634, 244], fill=(238, 234, 220, 255))  # 月亮
    # 湖面倒影
    refl = Image.new("RGBA", size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    for i in range(60):
        y = 430 + i * 6
        wdt = 120 * (1 - i / 70) + 14
        rd.ellipse([600 - wdt, y, 600 + wdt, y + 3], fill=(210, 205, 185, max(6, 60 - i)))
    img.alpha_composite(refl.filter(ImageFilter.GaussianBlur(2)))
    hills(img, 430, 26, (16, 24, 20), seed=52)
    save_jpg(add_grain(img.convert("RGB"), 7), os.path.join(GALLERY_DIR, "lake-moon.jpg"))


def photo_mountain_fog():
    size = (800, 1200)
    img = vgrad(size, [(0.0, (128, 140, 122)), (0.4, (88, 104, 88)), (1.0, (26, 38, 30))]).convert("RGBA")
    hills(img, 500, 120, (96, 110, 94), seed=61, blur=6)
    hills(img, 640, 100, (62, 78, 64), seed=62, blur=3)
    hills(img, 800, 80, (36, 52, 41), seed=63)
    hills(img, 980, 60, (20, 30, 24), seed=64)
    mist_bands(img, 480, 900, alpha=46)
    save_jpg(add_grain(img.convert("RGB"), 8), os.path.join(GALLERY_DIR, "mountain-fog.jpg"))


def photo_night_path():
    size = (1200, 800)
    img = vgrad(size, [(0.0, (10, 16, 14)), (0.6, (18, 28, 23)), (1.0, (26, 36, 29))]).convert("RGBA")
    stars(img, 520, ymax_ratio=0.55, seed=71)
    # 小路透视线
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.polygon([(520, 800), (680, 800), (618, 430), (588, 430)], fill=(52, 58, 44, 140))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(3)))
    glow(img, (604, 430), 90, GOLD, alpha=90)  # 路尽头一点灯
    hills(img, 430, 40, (14, 21, 17), seed=72)
    grass(img, 600, (40, 54, 42), count=500)
    save_jpg(add_grain(img.convert("RGB"), 7), os.path.join(GALLERY_DIR, "night-path.jpg"))


def photo_reeds_water():
    size = (800, 1200)
    img = vgrad(size, [(0.0, (104, 116, 92)), (0.45, (76, 92, 74)), (0.6, (52, 68, 56)), (1.0, (24, 36, 28))]).convert("RGBA")
    glow(img, (400, 380), 260, (214, 186, 122), alpha=70)
    # 水面微光
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    rnd = random.Random(81)
    for _ in range(160):
        x = rnd.uniform(0, 800)
        y = rnd.uniform(720, 1200)
        wdt = rnd.uniform(8, 60)
        ld.line([x - wdt, y, x + wdt, y], fill=(198, 196, 170, rnd.randint(10, 46)), width=1)
    img.alpha_composite(layer)
    # 芦苇
    for _ in range(220):
        x = rnd.uniform(0, 800)
        yb = rnd.uniform(820, 1200)
        ln = rnd.uniform(120, 420)
        tilt = rnd.uniform(-14, 14)
        col = lerp((36, 48, 38), (146, 132, 84), rnd.random() * 0.5)
        ld.line([x, yb, x + tilt, yb - ln], fill=col + (rnd.randint(120, 220),), width=2)
        if rnd.random() < 0.4:
            ex, ey = x + tilt, yb - ln
            ld.ellipse([ex - 3, ey - 12, ex + 3, ey + 4], fill=(122, 108, 68, 200))
    img.alpha_composite(layer)
    save_jpg(add_grain(img.convert("RGB"), 8), os.path.join(GALLERY_DIR, "reeds-water.jpg"))


def photo_valley_dawn():
    size = (1200, 800)
    img = vgrad(size, [(0.0, (70, 84, 72)), (0.35, (140, 132, 92)), (0.55, (196, 164, 104)), (1.0, (36, 50, 40))]).convert("RGBA")
    glow(img, (600, 430), 340, (240, 208, 138), alpha=140)
    hills(img, 470, 70, (74, 84, 62), seed=91, blur=4)
    hills(img, 560, 56, (46, 60, 46), seed=92)
    hills(img, 660, 40, (26, 38, 30), seed=93)
    mist_bands(img, 430, 600, alpha=40)
    grass(img, 690, (52, 66, 48), count=600)
    save_jpg(add_grain(img.convert("RGB"), 8), os.path.join(GALLERY_DIR, "valley-dawn.jpg"))


def photo_star_trail():
    size = (800, 1200)
    img = vgrad(size, [(0.0, (8, 13, 12)), (0.7, (16, 25, 21)), (1.0, (22, 32, 26))]).convert("RGBA")
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    cx, cy = 400, 420
    rnd = random.Random(101)
    for _ in range(260):
        r = rnd.uniform(40, 560)
        a0 = rnd.uniform(0, 6.28)
        span = rnd.uniform(0.15, 0.5)
        col = GOLD if rnd.random() < 0.15 else CREAM
        ld.arc([cx - r, cy - r, cx + r, cy + r],
               start=math.degrees(a0), end=math.degrees(a0 + span),
               fill=col + (rnd.randint(50, 140),), width=1)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.8)))
    hills(img, 960, 50, (12, 18, 15), seed=102)
    save_jpg(add_grain(img.convert("RGB"), 7), os.path.join(GALLERY_DIR, "star-trail.jpg"))


def photo_window_light():
    size = (1200, 800)
    img = vgrad(size, [(0.0, (30, 42, 34)), (1.0, (16, 24, 19))]).convert("RGBA")
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # 一扇透着暖光的窗 + 光柱
    ld.rectangle([840, 140, 1040, 420], fill=(222, 186, 116, 235))
    ld.rectangle([840, 140, 1040, 420], outline=(90, 76, 46, 255), width=8)
    ld.line([940, 140, 940, 420], fill=(90, 76, 46, 255), width=6)
    ld.line([840, 280, 1040, 280], fill=(90, 76, 46, 255), width=6)
    ld.polygon([(840, 420), (1040, 420), (1200, 800), (620, 800)], fill=(200, 170, 105, 34))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(2)))
    glow(img, (940, 280), 260, GOLD, alpha=80)
    save_jpg(add_grain(img.convert("RGB"), 9), os.path.join(GALLERY_DIR, "window-light.jpg"))


# ---------- 3. 关于页肖像（剪影） ----------
def portrait():
    size = (800, 1000)
    img = vgrad(size, [(0.0, (60, 74, 60)), (0.5, (96, 100, 72)), (0.8, (60, 70, 52)), (1.0, (24, 34, 27))]).convert("RGBA")
    glow(img, (560, 330), 300, (226, 194, 126), alpha=110)
    hills(img, 800, 50, (22, 32, 26), seed=111)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # 人物剪影（站立持相机）
    ld.ellipse([330, 300, 430, 404], fill=(14, 20, 17, 255))              # 头
    ld.polygon([(340, 400), (420, 400), (450, 640), (312, 640)], fill=(14, 20, 17, 255))  # 身
    ld.rectangle([336, 640, 372, 830], fill=(14, 20, 17, 255))            # 腿
    ld.rectangle([390, 640, 426, 830], fill=(14, 20, 17, 255))
    ld.rectangle([352, 428, 416, 470], fill=(10, 15, 12, 255))            # 相机
    ld.ellipse([374, 436, 396, 460], fill=(30, 40, 33, 255))              # 镜头
    ld.line([420, 430, 470, 520], fill=(14, 20, 17, 255), width=20)       # 手臂
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1)))
    grass(img, 830, (40, 54, 42), count=500, seed=112)
    save_jpg(add_grain(img.convert("RGB"), 8), os.path.join(IMG_DIR, "portrait.jpg"))


# ---------- 4. AI 视频占位短片 ----------
def make_videos():
    try:
        import imageio.v2 as imageio
    except Exception as e:
        print("imageio 不可用，跳过视频生成:", e)
        return

    W, H, FPS, SEC = 640, 360, 24, 6
    n = FPS * SEC

    def base_frame(t, hue_shift=0.0):
        """缓慢流动的雾渐变 + 漂浮光点。 t: 0~1"""
        y = np.linspace(0, 1, H)[:, None]
        x = np.linspace(0, 1, W)[None, :]
        wave = 0.12 * np.sin(x * 4 + t * 6.283 + hue_shift) + 0.08 * np.sin(x * 9 - t * 4)
        m = np.clip(y + wave, 0, 1)
        top = np.array([16, 26, 21], dtype=float)
        mid = np.array([40, 56, 45], dtype=float)
        bot = np.array([20, 30, 24], dtype=float)
        frame = np.zeros((H, W, 3), dtype=float)
        for c in range(3):
            frame[..., c] = np.where(m < 0.55,
                                     top[c] + (mid[c] - top[c]) * (m / 0.55),
                                     mid[c] + (bot[c] - mid[c]) * ((m - 0.55) / 0.45))
        return frame

    def particles(rnd, count, color):
        pts = []
        for _ in range(count):
            pts.append([rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 2.6),
                        rnd.uniform(0.2, 0.9), rnd.uniform(0, 6.28), color])
        return pts

    def render(path, pts, drift=(0, -6), hue_shift=0.0, poster=None):
        writer = imageio.get_writer(path, fps=FPS, codec="libx264",
                                    macro_block_size=None,
                                    ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart",
                                                   "-crf", "28", "-preset", "slow"])
        first = None
        for i in range(n):
            t = i / n
            frame = base_frame(t, hue_shift)
            for p in pts:
                p[0] = (p[0] + drift[0] * p[3]) % W
                p[1] = (p[1] + drift[1] * p[3]) % H
                r = p[2] * (1 + 0.3 * math.sin(t * 6.283 + p[4]))
                x0, y0 = float(p[0]), float(p[1])
                rr = int(max(r, 1)) + 1
                ys, ye = max(0, int(y0) - rr), min(H, int(y0) + rr + 1)
                xs, xe = max(0, int(x0) - rr), min(W, int(x0) + rr + 1)
                if ys >= ye or xs >= xe:
                    continue
                yy, xx = np.mgrid[ys:ye, xs:xe]
                dist = np.sqrt((yy - y0) ** 2 + (xx - x0) ** 2)
                mask = np.clip(1 - dist / max(r, 1e-3), 0, 1) ** 2 * 0.8
                patch = frame[ys:ye, xs:xe]
                for c in range(3):
                    patch[..., c] = patch[..., c] * (1 - mask) + p[5][c] * mask
                frame[ys:ye, xs:xe] = patch
            frame = np.clip(frame + np.random.normal(0, 1.2, frame.shape), 0, 255).astype(np.uint8)
            if first is None:
                first = frame.copy()
            writer.append_data(frame)
        writer.close()
        print("saved:", os.path.relpath(path, ROOT))
        if poster:
            Image.fromarray(first).save(poster, "JPEG", quality=86, optimize=True)
            print("saved:", os.path.relpath(poster, ROOT))

    rnd = random.Random(201)
    render(os.path.join(VIDEO_DIR, "dream-tide.mp4"),
           particles(rnd, 60, (214, 186, 122)), drift=(2, -5),
           poster=os.path.join(GALLERY_DIR, "dream-tide.jpg"))
    render(os.path.join(VIDEO_DIR, "cloud-machine.mp4"),
           particles(rnd, 90, (200, 210, 196)), drift=(6, 1), hue_shift=2.0,
           poster=os.path.join(GALLERY_DIR, "cloud-machine.jpg"))
    render(os.path.join(VIDEO_DIR, "neon-field.mp4"),
           particles(rnd, 70, (232, 214, 160)), drift=(0, -9), hue_shift=4.0,
           poster=os.path.join(GALLERY_DIR, "neon-field.jpg"))


if __name__ == "__main__":
    hero_nebula()
    photo_field_dusk()
    photo_mist_forest()
    photo_golden_wheat()
    photo_lake_moon()
    photo_mountain_fog()
    photo_night_path()
    photo_reeds_water()
    photo_valley_dawn()
    photo_star_trail()
    photo_window_light()
    portrait()
    make_videos()
    print("ALL DONE")
