# -*- coding: utf-8 -*-
"""第三批素材：
- 人像新系列：未晞 weixi 9、卷耳 juaner 9
- 风景 17 系列 x 5
- 静物：自由无用 ziyou 6、一两朵温柔色 wenrou 6
- 首页摄影入口横版 entry-photo.jpg
- 自动生成 assets/js/works-data.js（保留人文/AI视频文案，精选打 feat 标记）
"""
import math
import os
import random

from PIL import Image, ImageDraw

from generate_assets import (vgrad, glow, hills, stars, mist_bands, grass,
                             add_grain, save_jpg, lerp,
                             GOLD, GALLERY_DIR, IMG_DIR)
from generate_more import person, lantern, vine, SIL, SIL2

W, H = 900, 1350


# ============ 通用小元素 ============
def rock(d, x, y, w, h, color=SIL2):
    """一块不规则石头。"""
    d.polygon([(x - w / 2, y), (x - w * 0.42, y - h * 0.7), (x - w * 0.1, y - h),
               (x + w * 0.35, y - h * 0.8), (x + w / 2, y)], fill=color + (255,))


def tree(d, x, y, h, lean=0.0, color=SIL):
    """一棵简笔树（干 + 三两条枝）。"""
    top = (x + lean * h * 0.3, y - h)
    d.line([(x, y), top], fill=color + (255,), width=max(6, int(h * 0.045)))
    for a, ln in [(-0.9, 0.45), (0.7, 0.4), (-0.4, 0.3)]:
        bx = top[0] + math.cos(a) * h * ln
        by = top[1] + math.sin(a) * h * ln * 0.8
        d.line([top, (bx, by)], fill=color + (255,), width=max(4, int(h * 0.03)))


def dots(d, rnd, n, xr, yr, r, color, alpha=(140, 230)):
    """一簇色点（梅/樱/叶/雪/光斑）。"""
    for _ in range(n):
        x = rnd.uniform(*xr)
        y = rnd.uniform(*yr)
        rr = rnd.uniform(r * 0.5, r * 1.4)
        d.ellipse([x - rr, y - rr, x + rr, y + rr],
                  fill=color + (rnd.randint(*alpha),))


def moon_disc(img, x, y, r, color=(232, 222, 188)):
    d = ImageDraw.Draw(img)
    d.ellipse([x - r, y - r, x + r, y + r], fill=color + (235,))
    glow(img, (x, y), r * 2.6, color, alpha=50)


def water_band(d, y, color=(12, 20, 17)):
    d.rectangle([0, y, W, H], fill=color + (255,))


def safe_save(img, path, quality=84):
    """保护用户真照片：目标已存在且 >600KB 时跳过（只覆盖自己的占位图）。"""
    if os.path.exists(path) and os.path.getsize(path) > 600 * 1024:
        print("skip (用户真照片):", path)
        return
    save_jpg(img, path, quality=quality)


# ============ 1. 人像新系列（卷耳 juaner 已被用户上传真照片，不再生成） ============
def portrait_new():
    out = os.path.join(GALLERY_DIR, "portrait")
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(606)
    poses = [None, "up", "hold", "out", None, "hold", "up", None, "out"]
    hats = [None, "wide", None, None, "cap", None, "wide", None, None]

    cfgs = {
        # 未晞：天光未晞，黎明前青白微光
        "weixi": dict(stops=[(0.0, (14, 22, 22)), (0.5, (32, 46, 44)), (1.0, (20, 30, 26))],
                      glowc=(196, 210, 196), mist=True, stars_n=90),
    }
    for name, cfg in cfgs.items():
        for i in range(9):
            size = (W, H)
            img = vgrad(size, cfg["stops"]).convert("RGBA")
            gx = rnd.uniform(320, 580)
            gy = rnd.uniform(380, 540)
            glow(img, (gx, gy), rnd.uniform(220, 300), cfg["glowc"], alpha=70)
            if cfg.get("stars_n"):
                stars(img, cfg["stars_n"], ymax_ratio=0.45, seed=i * 3 + 11)
            hills(img, 900, 44, lerp(SIL, cfg["glowc"], 0.05), seed=i * 7 + 2)
            hills(img, 1050, 28, SIL, seed=i * 5 + 4)

            if cfg.get("rocks"):
                d = ImageDraw.Draw(img)
                for r_ in range(rnd.randint(2, 3)):
                    rock(d, rnd.uniform(120, 780), rnd.uniform(1150, 1330),
                         rnd.uniform(160, 320), rnd.uniform(90, 200))

            layer = Image.new("RGBA", size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            x = rnd.uniform(300, 600)
            ground_y = 1300 if cfg.get("rocks") else 1080
            hh = rnd.uniform(320, 420)
            head = person(ld, x, ground_y, hh, lean=rnd.uniform(-0.4, 0.4),
                          arm=poses[i], hat=hats[i])
            if poses[i] == "hold":
                lantern(img, int(head[0]), int(head[1] + hh * 0.32))
            img.alpha_composite(layer)

            if cfg.get("mist"):
                mist_bands(img, 800, 980, alpha=30)
            grass(img, ground_y + 40 if cfg.get("rocks") else 1060,
                  (40, 54, 40), count=400, seed=i + 8)
            safe_save(add_grain(img.convert("RGB"), 4),
                      os.path.join(out, "%s-%02d.jpg" % (name, i + 1)), quality=84)
    print("portrait_new done")


# ============ 2. 风景 17 系列 ============
# 每系列：目录名 -> (显示名, 配置)
LANDSCAPE = [
    ("mingxiaoling", "明孝陵 · 梅", "plum", 5),
    ("rousuilan", "揉碎蓝色", "blue", 7),
    ("qixiashan", "栖霞山 · 秋冬", "redleaf", 5),
    ("chuang", "窗", "window", 5),
    ("shanhubian", "山湖边", "lake", 5),
    ("wuxiang", "无想水镇 · 旧时唐风", "town", 5),
    ("yuantouzhu", "鼋头渚 · 樱", "sakura", 5),
    ("yuanmu", "缘木成鱼", "fish", 5),
    ("xizang", "西藏 · 往雪山走", "snow", 5),
    ("beifeng", "北风蹒跚", "wind", 2),
    ("liudong", "流动", "trail", 4),
    ("qingdao", "青岛 · 归梦", "sea", 4),
    ("feidi", "非敌", "duo", 5),
    ("chenruguang", "沉入光", "beam", 3),
    ("yuese", "月色", "moon", 5),
    ("zhanyou", "占有月亮", "reach", 5),
    ("chunlv", "春绿", "sprout", 3),
]


def landscape_series():
    for idx, (slug, _cn, kind, _limit) in enumerate(LANDSCAPE):
        out = os.path.join(GALLERY_DIR, "landscape", slug)
        os.makedirs(out, exist_ok=True)
        rnd = random.Random(700 + idx * 13)
        for i in range(5):
            size = (W, H)
            img = render_landscape(size, kind, rnd, i)
            safe_save(add_grain(img.convert("RGB"), 4),
                      os.path.join(out, "%s-%02d.jpg" % (slug, i + 1)), quality=84)
    print("landscape 17 series done")


def render_landscape(size, kind, rnd, i):
    base_sky = [(0.0, (14, 22, 18)), (0.55, (26, 40, 32)), (1.0, (18, 28, 23))]
    sky = {
        "snow":   [(0.0, (16, 26, 34)), (0.5, (34, 52, 64)), (1.0, (20, 32, 40))],
        "sea":    [(0.0, (12, 24, 30)), (0.55, (24, 44, 52)), (1.0, (16, 30, 36))],
        "beam":   [(0.0, (20, 28, 22)), (0.5, (48, 52, 34)), (1.0, (22, 32, 25))],
        "moon":   [(0.0, (8, 14, 16)), (0.6, (16, 28, 30)), (1.0, (12, 20, 22))],
        "sakura": [(0.0, (24, 28, 26)), (0.5, (48, 48, 42)), (1.0, (26, 34, 28))],
        "sprout": [(0.0, (20, 32, 24)), (0.55, (44, 62, 38)), (1.0, (24, 38, 28))],
        "blue":   [(0.0, (10, 16, 26)), (0.6, (18, 30, 46)), (1.0, (12, 20, 32))],
        "town":   [(0.0, (16, 22, 18)), (0.6, (30, 38, 28)), (1.0, (20, 28, 22))],
        "wind":   [(0.0, (26, 28, 20)), (0.55, (48, 46, 30)), (1.0, (28, 30, 22))],
        "redleaf": [(0.0, (22, 24, 18)), (0.5, (52, 44, 28)), (1.0, (26, 28, 20))],
    }.get(kind, base_sky)

    img = vgrad(size, sky).convert("RGBA")
    d = ImageDraw.Draw(img)
    glowc = {
        "beam": (224, 190, 116), "moon": (228, 216, 178), "sakura": (228, 178, 168),
        "sprout": (168, 200, 128), "blue": (120, 160, 220), "town": (214, 176, 108),
        "sea": (150, 190, 200), "snow": (200, 214, 224),
    }.get(kind, (200, 178, 120))
    gx = rnd.uniform(300, 600)
    gy = rnd.uniform(320, 620)
    glow(img, (gx, gy), rnd.uniform(220, 320), glowc, alpha=60)

    # ---- 地平线/山水骨架 ----
    if kind in ("sea", "lake", "fish", "sakura"):
        wy = int(H * rnd.uniform(0.58, 0.66))
        hills(img, wy - 30, 36, SIL2, seed=i + 3)
        water_band(d, wy, (10, 18, 20) if kind == "sea" else (12, 20, 17))
        for k in range(18):   # 水面碎光
            t = k / 17
            yy = wy + 10 + t * (H - wy - 30)
            ww = rnd.uniform(20, 90) * (1 - t * 0.5)
            d.line([(gx - ww, yy), (gx + ww, yy)],
                   fill=glowc + (int(70 * (1 - t)) + 10,), width=2)
    elif kind == "snow":
        d.polygon([(80, 900), (360, 480), (560, 900)], fill=(210, 220, 228, 60))
        d.polygon([(420, 900), (700, 540), (900, 900)], fill=(200, 212, 222, 46))
        hills(img, 980, 30, SIL, seed=i + 5)
    elif kind in ("wind", "redleaf", "plum", "sprout", "duo", "reach", "trail", "beam", "blue", "town", "window", "moon"):
        hills(img, int(H * 0.68), 42, SIL2, seed=i + 7)
        hills(img, int(H * 0.78), 26, SIL, seed=i + 9)

    # ---- 系列特征元素 ----
    if kind == "plum":
        for t_ in range(rnd.randint(2, 3)):
            tree(d, rnd.uniform(150, 750), rnd.uniform(1080, 1260), rnd.uniform(300, 460),
                 lean=rnd.uniform(-0.6, 0.6))
        dots(d, rnd, 90, (60, 840), (330, 900), 7, (196, 92, 92))
        dots(d, rnd, 40, (60, 840), (330, 900), 4, (226, 150, 140))
    elif kind == "snow":
        # 经幡：几组斜线彩条
        for f in range(2):
            x0, y0 = rnd.uniform(80, 500), rnd.uniform(560, 760)
            x1, y1 = x0 + rnd.uniform(220, 380), y0 + rnd.uniform(-60, 60)
            d.line([(x0, y0), (x1, y1)], fill=(220, 220, 210, 120), width=2)
            for k in range(7):
                t = k / 6
                fx, fy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                col = [(200, 90, 80), (90, 130, 190), (220, 190, 90), (90, 160, 110), (220, 220, 210)][k % 5]
                d.polygon([(fx, fy), (fx + 16, fy + 4), (fx + 12, fy + 26)], fill=col + (190,))
        dots(d, rnd, 120, (0, 900), (0, 1350), 2.5, (235, 240, 245), (60, 140))
    elif kind == "fish":
        # 倒木横斜 + 鱼形光斑
        d.line([(120, 1080), (700, 960)], fill=SIL + (255,), width=18)
        d.line([(300, 1150), (820, 1100)], fill=SIL2 + (255,), width=12)
        for f in range(6):
            fx, fy = rnd.uniform(180, 760), rnd.uniform(900, 1240)
            d.ellipse([fx - 14, fy - 5, fx + 14, fy + 5], fill=glowc + (120,))
            d.polygon([(fx + 12, fy), (fx + 24, fy - 7), (fx + 24, fy + 7)], fill=glowc + (100,))
    elif kind == "wind":
        tree(d, rnd.uniform(560, 700), 1180, rnd.uniform(380, 480), lean=0.8)
        grass(img, 1120, (70, 64, 38), count=520, seed=i + 12)
        for s in range(26):   # 风的斜线
            x0, y0 = rnd.uniform(0, 800), rnd.uniform(300, 1100)
            d.line([(x0, y0), (x0 + rnd.uniform(80, 200), y0 + rnd.uniform(14, 40))],
                   fill=(190, 180, 130, 36), width=3)
    elif kind == "trail":
        for t_ in range(4):
            y0 = rnd.uniform(760, 1160)
            pts = [(k * 30, y0 + math.sin(k / 3 + t_) * 26) for k in range(31)]
            d.line(pts, fill=(214, 186, 110, 120 - t_ * 22), width=4)
        stars(img, 200, ymax_ratio=0.5, seed=i + 15)
    elif kind == "town":
        # 水乡屋檐 + 一串暖灯
        for b in range(3):
            bx = 60 + b * 300 + rnd.uniform(-30, 30)
            by = rnd.uniform(700, 880)
            d.polygon([(bx, by), (bx + 130, by - 60), (bx + 260, by)], fill=SIL + (255,))
            d.rectangle([bx + 20, by, bx + 240, by + 190], fill=SIL2 + (255,))
        for l in range(5):
            lx = rnd.uniform(100, 800)
            ly = rnd.uniform(880, 980)
            lantern(img, int(lx), int(ly), r=12)
        water_band(d, 1100, (12, 18, 15))
        for k in range(10):
            d.line([(rnd.uniform(100, 800), 1120 + k * 20), (rnd.uniform(100, 800), 1120 + k * 20)],
                   fill=(214, 176, 108, 60), width=3)
    elif kind == "duo":
        tree(d, 280, 1200, rnd.uniform(420, 520), lean=0.3)
        tree(d, 640, 1210, rnd.uniform(380, 480), lean=-0.3)
        mist_bands(img, 1000, 1140, alpha=24)
    elif kind == "sea":
        # 一叶帆
        sx = rnd.uniform(280, 620)
        sy = int(H * 0.62)
        d.polygon([(sx, sy), (sx, sy - 120), (sx + 60, sy - 10)], fill=(226, 224, 210, 190))
        d.line([(sx - 30, sy), (sx + 70, sy)], fill=SIL + (255,), width=6)
        stars(img, 160, ymax_ratio=0.4, seed=i + 18)
    elif kind == "beam":
        for b in range(3):   # 云隙光束
            bx = gx - 120 + b * 130
            d.polygon([(bx, 300), (bx + 90, 300), (bx + 200, 1100), (bx + 60, 1100)],
                      fill=(224, 196, 130, 26))
        grass(img, 1140, (56, 54, 32), count=460, seed=i + 20)
    elif kind == "moon":
        moon_disc(img, gx, gy, rnd.uniform(56, 80))
        tree(d, rnd.uniform(180, 300), 1200, 360, lean=0.2)
        stars(img, 420, ymax_ratio=0.6, seed=i + 21)
    elif kind == "redleaf":
        for t_ in range(2):
            tree(d, rnd.uniform(180, 720), rnd.uniform(1100, 1240), rnd.uniform(340, 460),
                 lean=rnd.uniform(-0.4, 0.4))
        dots(d, rnd, 100, (60, 840), (360, 960), 8, (188, 92, 60))
        dots(d, rnd, 60, (60, 840), (360, 960), 5, (216, 140, 70))
    elif kind == "lake":
        moon_disc(img, gx, gy, 40)
        stars(img, 300, ymax_ratio=0.5, seed=i + 23)
    elif kind == "window":
        wx0, wy0 = W / 2 - 140, 300
        d.rectangle([wx0, wy0, wx0 + 280, wy0 + 420], fill=(216, 184, 120, 190))
        d.line([(W / 2, wy0), (W / 2, wy0 + 420)], fill=SIL + (255,), width=8)
        d.line([(wx0, wy0 + 210), (wx0 + 280, wy0 + 210)], fill=SIL + (255,), width=8)
        for v in range(3):
            vine(img, rnd.uniform(80, 820), 0, rnd.uniform(200, 420), seed=i * 5 + v)
        d.rectangle([0, 1050, W, H], fill=(16, 24, 19, 255))
    elif kind == "sakura":
        for t_ in range(2):
            tree(d, rnd.uniform(200, 700), rnd.uniform(820, 940), rnd.uniform(360, 480),
                 lean=rnd.uniform(-0.5, 0.5))
        dots(d, rnd, 130, (40, 860), (300, 900), 8, (228, 170, 165))
        dots(d, rnd, 60, (40, 860), (300, 900), 5, (244, 205, 195))
    elif kind == "reach":
        moon_disc(img, gx, gy - 100, 62)
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        person(ld, W / 2, 1210, 400, arm="up")
        img.alpha_composite(layer)
        stars(img, 380, ymax_ratio=0.55, seed=i + 26)
    elif kind == "sprout":
        grass(img, 1080, (96, 130, 70), count=620, seed=i + 28)
        dots(d, rnd, 50, (60, 840), (700, 1150), 4, (150, 190, 100))
        mist_bands(img, 820, 960, alpha=26)
    elif kind == "blue":
        for b in range(30):   # 揉碎的蓝色光斑
            glow(img, (rnd.uniform(60, 840), rnd.uniform(400, 1200)),
                 rnd.uniform(14, 46), (110, 150, 220), alpha=rnd.randint(36, 90))
        stars(img, 240, ymax_ratio=0.4, gold_ratio=0.05, seed=i + 30)
    else:
        stars(img, 240, ymax_ratio=0.5, seed=i + 32)
    return img


# ============ 3. 静物 2 系列 ============
def stilllife_new():
    specs = [("ziyou", 6, 808), ("wenrou", 6, 909)]
    for slug, n, seed0 in specs:
        out = os.path.join(GALLERY_DIR, "stilllife", slug)
        os.makedirs(out, exist_ok=True)
        rnd = random.Random(seed0)
        for i in range(n):
            size = (W, H)
            if slug == "ziyou":
                stops = [(0.0, (26, 36, 30)), (0.6, (36, 48, 38)), (1.0, (20, 30, 24))]
            else:
                stops = [(0.0, (38, 44, 38)), (0.55, (56, 60, 48)), (1.0, (28, 36, 30))]
            img = vgrad(size, stops).convert("RGBA")
            d = ImageDraw.Draw(img)
            # 背景窗光
            wx0, wy0 = rnd.uniform(220, 380), rnd.uniform(160, 260)
            warm = (216, 188, 128) if slug == "wenrou" else (200, 178, 118)
            glow(img, (wx0, wy0 + 160), 280, warm, alpha=70 if slug == "wenrou" else 50)
            ty = 1050
            d.rectangle([0, ty, W, H], fill=(18, 26, 21, 255))
            kind = i % 6
            cx = W / 2
            if kind == 0:    # 瓶中枝
                d.polygon([(cx - 32, ty), (cx + 32, ty), (cx + 22, ty - 190), (cx - 22, ty - 190)],
                          fill=SIL + (255,))
                for b in range(5):
                    a = math.radians(-90 + (b - 2) * 22)
                    ln = rnd.uniform(150, 250)
                    ex, ey = cx + ln * math.cos(a) * 0.7, (ty - 190) + ln * math.sin(a)
                    d.line([(cx, ty - 190), (ex, ey)], fill=SIL + (255,), width=4)
                    col = (232, 200, 180) if slug == "wenrou" else SIL2
                    d.ellipse([ex - 9, ey - 6, ex + 9, ey + 6], fill=col + (255,))
            elif kind == 1:  # 茶烟
                d.rectangle([cx - 55, ty - 95, cx + 55, ty], fill=SIL + (255,))
                d.arc([cx + 45, ty - 75, cx + 100, ty - 25], -90, 90, fill=SIL + (255,), width=10)
                for s in range(3):
                    pts = [(cx - 20 + s * 22 + 14 * math.sin(k / 19 * 4 + s),
                            ty - 115 - k / 19 * 190) for k in range(20)]
                    d.line(pts, fill=(170, 180, 168, 90), width=3)
            elif kind == 2:  # 书堆
                for b in range(4):
                    bw = rnd.uniform(190, 250)
                    d.rectangle([cx - bw / 2, ty - 36 * (b + 1), cx + bw / 2, ty - 36 * b],
                                fill=(SIL if b % 2 else SIL2) + (255,))
            elif kind == 3:  # 空椅
                d.rectangle([cx - 110, ty - 270, cx - 90, ty], fill=SIL + (255,))
                d.rectangle([cx + 90, ty - 270, cx + 110, ty], fill=SIL + (255,))
                d.rectangle([cx - 120, ty - 310, cx + 120, ty - 270], fill=SIL + (255,))
                d.rectangle([cx - 110, ty - 500, cx - 90, ty - 310], fill=SIL + (255,))
            elif kind == 4:  # 小盆栽
                d.polygon([(cx - 44, ty), (cx + 44, ty), (cx + 30, ty - 115), (cx - 30, ty - 115)],
                          fill=SIL + (255,))
                for b in range(6):
                    a = math.radians(-90 + (b - 2.5) * 18)
                    ln = rnd.uniform(95, 170)
                    ex, ey = cx + ln * math.cos(a) * 0.8, (ty - 115) + ln * math.sin(a)
                    d.line([(cx, ty - 115), (ex, ey)], fill=SIL + (255,), width=5)
                    col = (170, 200, 140) if slug == "wenrou" else SIL
                    d.ellipse([ex - 11, ey - 7, ex + 11, ey + 7], fill=col + (255,))
            else:            # 一两朵温柔色：单枝小花 / 自由无用：枯枝横瓶
                if slug == "wenrou":
                    d.line([(cx, ty), (cx - 10, ty - 260)], fill=SIL + (255,), width=5)
                    for p_ in range(7):
                        a = math.radians(p_ * 51)
                        px, py = cx - 10 + 26 * math.cos(a), ty - 260 + 26 * math.sin(a)
                        d.ellipse([px - 14, py - 10, px + 14, py + 10], fill=(238, 205, 185, 235))
                    d.ellipse([cx - 22, ty - 272, cx + 2, ty - 248], fill=(226, 178, 96, 255))
                else:
                    d.polygon([(cx - 120, ty), (cx + 120, ty), (cx + 100, ty - 60), (cx - 100, ty - 60)],
                              fill=SIL2 + (255,))
                    d.line([(cx - 140, ty - 130), (cx + 160, ty - 200)], fill=SIL + (255,), width=5)
            safe_save(add_grain(img.convert("RGB"), 4),
                      os.path.join(out, "%s-%02d.jpg" % (slug, i + 1)), quality=84)
    print("stilllife done")


# ============ 4. 首页摄影入口横版图 ============
def entry_photo():
    size = (1600, 1067)
    img = vgrad(size, [(0.0, (12, 20, 17)), (0.55, (28, 42, 34)), (1.0, (18, 28, 22))]).convert("RGBA")
    glow(img, (1050, 380), 330, GOLD, alpha=70)
    stars(img, 700, ymax_ratio=0.6, gold_ratio=0.14, seed=51)
    hills(img, 720, 60, SIL2, seed=52)
    hills(img, 830, 40, SIL, seed=53)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    head = person(ld, 800, 950, 420, lean=0.1, arm="hold")
    img.alpha_composite(layer)
    lantern(img, int(head[0]), int(head[1] + 130))
    grass(img, 950, (40, 54, 38), count=520, seed=54)
    save_jpg(add_grain(img.convert("RGB"), 3),
             os.path.join(IMG_DIR, "entry-photo.jpg"), quality=88)
    print("entry-photo done")


# ============ 5. 输出 works-data.js（扫描驱动：以文件夹实际内容为准） ============
# 卷耳 11 个子组（sub 显示名带括号，文件夹名为对应汉字）；页面展示顺序从上到下（十一）→（一）
JUANER_ORDER = ["（十一）", "（十）", "（八）", "（九）", "（七）", "（六）",
                "（五）", "（四）", "（三）", "（二）", "（一）"]

CN_NUMS = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]


def scan_imgs(folder, real_only=False):
    """列出文件夹里的图片文件（按文件名排序）。
    real_only=True 时过滤生成占位图。占位判定：<=600KB **且** 修改时间在
    2026-07-27 之后（生成脚本批次）——用户的老照片虽体积小但 mtime 早，不误杀。"""
    p = os.path.join(GALLERY_DIR, folder)
    if not os.path.isdir(p):
        return []
    gen_epoch = 1753632000  # 2026-07-27 12:00 UTC，生成占位图的时间分界
    out = []
    for f in sorted(os.listdir(p)):
        fp = os.path.join(p, f)
        if not os.path.isfile(fp) or not f.lower().endswith((".jpg", ".jpeg")):
            continue
        if real_only:
            small = os.path.getsize(fp) <= 600 * 1024
            recent = os.path.getmtime(fp) >= gen_epoch
            if small and recent:
                continue  # 生成占位
        out.append(f)
    return out


def emit_works_data():
    P = "assets/img/gallery"
    lines = []
    lines.append("/* 作品数据（本文件由 tools/gen_series.py 扫描文件夹自动生成，可手工编辑）")
    lines.append("   cat：portrait 人像 / landscape 风景 / humanity 人文 / stilllife 静物 / video AI 视频")
    lines.append("        featured 精选（独立于各栏目的单独挑选，图片在 gallery/featured/）")
    lines.append("   series：系列名；sub：系列内子组（如卷耳的（一）~（十一））")
    lines.append("   group：精选条目所属组（portrait/landscape/humanity/stilllife）")
    lines.append("   横屏照片：程序自动识别真实方向，无需设置。")
    lines.append("   增删照片：在对应文件夹里增删文件后，重新运行 tools/gen_series.py 即可同步清单。")
    lines.append("*/")
    lines.append("window.WORKS = [")

    def item(cat, src, title, desc, series=None, sub=None, group=None):
        s = '  { type: "photo", cat: "%s", ' % cat
        if series:
            s += 'series: "%s", ' % series
        if sub:
            s += 'sub: "%s", ' % sub
        if group:
            s += 'group: "%s", ' % group
        s += 'src: "%s/%s", title: "%s", desc: "%s" },' % (P, src, title, desc)
        lines.append(s)

    def num(i):
        return CN_NUMS[i] if i < len(CN_NUMS) else str(i + 1)

    # ---- 精选（独立挑选；只展示已上传的真照片）----
    lines.append("  /* ===== 精选（单独挑选，featured/ 目录，同名覆盖即可更换） ===== */")
    for group, gname in [("portrait", "人像"), ("landscape", "风景"),
                         ("humanity", "人文"), ("stilllife", "静物"), ("meow", "喵星人")]:
        files = [f for f in scan_imgs("featured", real_only=True) if f.startswith(group + "-")][:9]
        for i, f in enumerate(files):
            item("featured", "featured/" + f, "精选%s · %s" % (gname, num(i)), "", group=group)

    # ---- 人像：未晞 / 自若 / 蔓生 / 序章（只展示已上传的真照片） ----
    for skey, slug in [("未晞", "weixi"), ("自若", "ziruo"), ("蔓生", "mansheng"), ("序章", "xuzhang")]:
        files = [f for f in scan_imgs("portrait", real_only=True) if f.startswith(slug + "-")]
        if not files:
            continue
        lines.append("  /* ===== 人像 · %s ===== */" % skey)
        for i, f in enumerate(files):
            item("portrait", "portrait/" + f, "%s · %s" % (skey, num(i)), "", series=skey)

    # ---- 人像 · 卷耳（扫描 portrait/juaner/汉字子目录） ----
    lines.append("  /* ===== 人像 · 卷耳 ===== */")
    for sub_name in JUANER_ORDER:
        folder_name = sub_name.strip("（）")
        files = scan_imgs(os.path.join("portrait", "juaner", folder_name), real_only=True)
        for i, f in enumerate(files):
            item("portrait", "portrait/juaner/%s/%s" % (folder_name, f),
                 "%s" % num(i), "", series="卷耳", sub=sub_name)

    # ---- 风景 17 系列（按 LANDSCAPE 顺序与数量上限；只展示已上传的真照片） ----
    for slug, cn, _kind, limit in LANDSCAPE:
        files = scan_imgs(os.path.join("landscape", slug), real_only=True)[:limit]
        if not files:
            continue
        lines.append("  /* ===== 风景 · %s ===== */" % cn)
        for i, f in enumerate(files):
            item("landscape", "landscape/%s/%s" % (slug, f), "%s · %s" % (cn, num(i)), "", series=cn)

    # ---- 人文（序号化标题） ----
    lines.append("  /* ===== 人文 ===== */")
    for i, f in enumerate(scan_imgs("humanity", real_only=True)):
        item("humanity", "humanity/" + f, "人文 · %s" % num(i), "")

    # ---- 静物 2 系列（ziyou=冬日迟暮 限 4 张；只展示已上传的真照片） ----
    for slug, cn, limit in [("ziyou", "冬日迟暮", 4), ("wenrou", "一两朵温柔色", 99)]:
        files = scan_imgs(os.path.join("stilllife", slug), real_only=True)[:limit]
        if not files:
            continue
        lines.append("  /* ===== 静物 · %s ===== */" % cn)
        for i, f in enumerate(files):
            item("stilllife", "stilllife/%s/%s" % (slug, f), "%s · %s" % (cn, num(i)), "", series=cn)

    # ---- 喵星人（占位图也显示，作为预留位置；用户传照片后自动替换） ----
    meow_files = scan_imgs("meow")
    if meow_files:
        lines.append("  /* ===== 喵星人 ===== */")
        for i, f in enumerate(meow_files):
            item("meow", "meow/" + f, "喵星人 · %s" % num(i), "")

    # ---- AI 视频（封面在 gallery/AI/，视频在 assets/videos/，同名配对；容忍文件名前缀） ----
    lines.append("  /* ===== AI 视频 ===== */")
    video_order = ["卷耳 · 国风 · 园林", "蔓生 · 情绪 · 森林",
                   "未晞 · 情绪 · 室内", "自若 · 情绪 · 山谷", "卷耳 · 日系 · 小院"]

    def find_suffix(d, suffix):
        """在目录里找以 suffix 结尾的文件（容忍用户加的排序前缀如 1未晞…）。"""
        if not os.path.isdir(d):
            return None
        for f in sorted(os.listdir(d)):
            if f.endswith(suffix):
                return f
        return None

    videos_dir = os.path.normpath(os.path.join(os.path.dirname(GALLERY_DIR), "..", "videos"))
    for name in video_order:
        cover = find_suffix(os.path.join(GALLERY_DIR, "AI"), name + ".jpg")
        vid = find_suffix(videos_dir, name + ".mp4")
        if not (cover and vid):
            continue
        lines.append('  { type: "video", cat: "video", src: "%s/AI/%s", video: "assets/videos/%s", title: "%s", desc: "" },'
                     % (P, cover, vid, name))
    lines.append("];")
    lines.append("")
    lines.append("/* 一级分类 */")
    lines.append('window.CATS = [')
    lines.append('  { key: "portrait",  name: "人像" },')
    lines.append('  { key: "landscape", name: "风景" },')
    lines.append('  { key: "humanity",  name: "人文" },')
    lines.append('  { key: "stilllife", name: "静物" },')
    lines.append('  { key: "meow",      name: "喵星人" }')
    lines.append("];")
    lines.append("")
    lines.append("/* 各分类的系列（顺序即页面展示顺序）；sub 为系列诗句/副题；")
    lines.append("   children 为系列内子组（卷耳：页面从上到下（十一）→（一）） */")
    lines.append("window.SERIES = {")
    lines.append('  portrait: [')
    lines.append('    { key: "未晞", sub: "野有蔓草，天光未晞" },')
    lines.append('    { key: "自若", sub: "野有蔓草，其华自若" },')
    lines.append('    { key: "蔓生", sub: "萋萋其野" },')
    lines.append('    { key: "序章", sub: "凡是过往，皆为序章" },')
    lines.append('    { key: "卷耳", sub: "于彼石隙", children: [%s] }'
                 % ", ".join('"%s"' % s for s in JUANER_ORDER))
    lines.append("  ],")
    lines.append("  landscape: [")
    for slug, cn, _k, _l in LANDSCAPE:
        lines.append('    { key: "%s" },' % cn)
    lines.append("  ],")
    lines.append('  stilllife: [')
    lines.append('    { key: "冬日迟暮" },')
    lines.append('    { key: "一两朵温柔色" }')
    lines.append("  ]")
    lines.append("};")

    out = os.path.join(os.path.dirname(GALLERY_DIR), "..", "js", "works-data.js")
    out = os.path.normpath(out)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("works-data.js written:", out)


if __name__ == "__main__":
    portrait_new()
    landscape_series()
    stilllife_new()
    entry_photo()
    emit_works_data()
    print("ALL DONE")
