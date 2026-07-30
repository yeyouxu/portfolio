# -*- coding: utf-8 -*-
"""第二批素材：高清星空、女孩剪影、人像三系列、人文、静物。"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from generate_assets import (vgrad, glow, hills, stars, mist_bands, grass,
                             add_grain, save_jpg, lerp,
                             DEEP, PINE, MOSS, SAGE, MIST, GOLD, CREAM, NIGHT,
                             IMG_DIR, GALLERY_DIR)

random.seed(77)
np.random.seed(77)

SIL = (11, 16, 13)          # 剪影色：近黑的绿
SIL2 = (16, 22, 18)


# ---------- 1. 高清星空背景（低噪点） ----------
def hero_hd():
    size = (2560, 1440)
    img = vgrad(size, [(0.0, (9, 15, 13)), (0.5, (14, 22, 18)), (1.0, (22, 32, 26))]).convert("RGBA")
    neb = Image.new("RGBA", size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(neb)
    rnd = random.Random(31)
    for _ in range(14):
        cx = rnd.uniform(0, 2560)
        cy = rnd.uniform(0, 950)
        rx = rnd.uniform(260, 640)
        ry = rx * rnd.uniform(0.28, 0.55)
        col = [(44, 62, 50), (56, 62, 42), (36, 52, 44), (60, 58, 40)][rnd.randrange(4)]
        nd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col + (20,))
    neb = neb.filter(ImageFilter.GaussianBlur(130))
    img.alpha_composite(neb)
    glow(img, (2050, 300), 340, GOLD, alpha=46)
    glow(img, (500, 620), 420, (70, 90, 70), alpha=36)
    # 更细腻的星层：大量小星 + 少量亮星
    stars(img, 1500, ymax_ratio=0.95, gold_ratio=0.10, seed=41)
    stars(img, 260, ymax_ratio=0.9, gold_ratio=0.22, seed=42)
    # 噪点收敛到 2，画面更干净
    img = add_grain(img.convert("RGB"), 2)
    save_jpg(img, os.path.join(IMG_DIR, "hero-nebula.jpg"), quality=90)


# ---------- 2. 女孩剪影（透明 PNG） ----------
# 手电筒尖端锚点（图像坐标），stars.js 会用同一组数
GIRL_W, GIRL_H = 700, 900
ANCHOR = (543, 264)


def girl_field():
    img = Image.new("RGBA", (GIRL_W, GIRL_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 地面：一条缓缓起伏的原野曲线
    ground = []
    for x in range(-20, GIRL_W + 20, 10):
        y = 812 + 10 * math.sin(x * 0.008) + 4 * math.sin(x * 0.02)
        ground.append((x, y))
    d.polygon(ground + [(GIRL_W + 20, GIRL_H), (-20, GIRL_H)], fill=SIL + (255,))

    cx = 330  # 女孩中轴
    # 长裙（A 字）
    d.polygon([(cx - 42, 470), (cx + 42, 470), (cx + 108, 806), (cx - 108, 806)], fill=SIL + (255,))
    # 上身
    d.polygon([(cx - 56, 396), (cx + 56, 396), (cx + 44, 478), (cx - 44, 478)], fill=SIL + (255,))
    # 头
    d.ellipse([cx - 38, 288, cx + 38, 366], fill=SIL + (255,))
    # 长发（背影，垂到腰际，微微左飘）
    hair = [(cx - 40, 300), (cx + 34, 296), (cx + 46, 400), (cx + 30, 512),
            (cx + 2, 540), (cx - 34, 520), (cx - 52, 420), (cx - 56, 330)]
    d.polygon(hair, fill=SIL2 + (255,))
    # 左臂自然下垂
    d.line([(cx - 50, 410), (cx - 66, 520)], fill=SIL + (255,), width=26)
    # 右臂举起：肩(375,400)→肘(440,350)→手(505,290)
    d.line([(375, 402), (440, 350)], fill=SIL + (255,), width=26)
    d.line([(440, 350), (505, 290)], fill=SIL + (255,), width=22)
    # 手 + 手电筒（筒身斜向上 35°，尖端即 ANCHOR）
    ang = math.radians(-35)
    hx, hy = 505, 290
    tx, ty = hx + 46 * math.cos(ang), hy + 46 * math.sin(ang)
    d.ellipse([hx - 12, hy - 12, hx + 12, hy + 12], fill=SIL + (255,))
    d.line([(hx, hy), (tx, ty)], fill=SIL + (255,), width=20)
    d.ellipse([tx - 11, ty - 11, tx + 11, ty + 11], fill=SIL + (255,))

    # 一株草（右侧，六七片弯叶）
    bx, by = 585, 812
    rnd = random.Random(9)
    for i in range(7):
        a = -90 + (i - 3) * 16 + rnd.uniform(-4, 4)
        ln = rnd.uniform(56, 112)
        ar = math.radians(a)
        midx = bx + ln * 0.5 * math.cos(ar) + rnd.uniform(-6, 6)
        midy = by + ln * 0.55 * math.sin(ar)
        ex = bx + ln * math.cos(ar) * 0.9
        ey = by + ln * math.sin(ar)
        d.line([(bx, by), (midx, midy), (ex, ey)], fill=SIL + (255,), width=4, joint="curve")

    # 手电筒玻璃一点微光
    glow(img, (int(tx), int(ty)), 26, GOLD, alpha=110)

    img.save(os.path.join(IMG_DIR, "girl-field.png"))
    print("saved: assets/img/girl-field.png  anchor =", ANCHOR)


# ---------- 3. 通用小人剪影 ----------
def person(d, x, y, h, lean=0.0, arm=None, hat=None, color=SIL):
    """风格化人物剪影。 y=脚底, h=身高"""
    hr = h * 0.072                       # 头半径
    hy = y - h + hr                      # 头中心 y
    lx = x + lean * h * 0.12
    # 脖颈：头与身相连
    d.rectangle([lx - hr * 0.4, hy + hr * 0.4, lx + hr * 0.4, hy + hr * 1.5], fill=color + (255,))
    d.ellipse([lx - hr, hy - hr, lx + hr, hy + hr], fill=color + (255,))
    if hat == "wide":
        d.ellipse([lx - hr * 1.9, hy - hr * 0.9, lx + hr * 1.9, hy - hr * 0.1], fill=color + (255,))
    elif hat == "cap":
        d.pieslice([lx - hr, hy - hr * 1.15, lx + hr, hy + hr * 0.7], 180, 360, fill=color + (255,))
    sh_y = hy + hr * 1.1                  # 肩
    hip_y = y - h * 0.38
    # 躯干：宽肩收腰
    d.polygon([(lx - h * 0.115, sh_y), (lx + h * 0.115, sh_y),
               (x + h * 0.07, hip_y), (x - h * 0.07, hip_y)], fill=color + (255,))
    # 下摆（长外套/裙，自腰放宽）
    d.polygon([(x - h * 0.07, hip_y), (x + h * 0.07, hip_y),
               (x + h * 0.16, y), (x - h * 0.16, y)], fill=color + (255,))
    if arm == "up":      # 一手举向天空
        d.line([(lx + h * 0.1, sh_y + 4), (lx + h * 0.22, sh_y - h * 0.18)], fill=color + (255,), width=int(h * 0.05))
    elif arm == "out":   # 双臂微张
        d.line([(lx - h * 0.1, sh_y + 4), (lx - h * 0.22, sh_y + h * 0.12)], fill=color + (255,), width=int(h * 0.05))
        d.line([(lx + h * 0.1, sh_y + 4), (lx + h * 0.22, sh_y + h * 0.12)], fill=color + (255,), width=int(h * 0.05))
    elif arm == "hold":  # 双手持物于胸前
        d.line([(lx - h * 0.09, sh_y + 4), (lx, sh_y + h * 0.15)], fill=color + (255,), width=int(h * 0.045))
        d.line([(lx + h * 0.09, sh_y + 4), (lx, sh_y + h * 0.15)], fill=color + (255,), width=int(h * 0.045))
    return (lx, hy)       # 返回头中心，便于加道具光


def lantern(img, x, y, r=14):
    d = ImageDraw.Draw(img)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(222, 186, 116, 255))
    glow(img, (x, y), r * 4, GOLD, alpha=90)


# ---------- 4. 人像三系列 ----------
SERIES = {
    "xuzhang": dict(   # 序章：破晓的金绿，一切刚开始
        stops=[(0.0, (52, 62, 46)), (0.45, (116, 108, 66)), (0.72, (150, 126, 74)), (1.0, (34, 44, 34))],
        glowc=(236, 200, 130), dir="portrait"),
    "mansheng": dict(  # 蔓生：浓绿与植物，安静地生长
        stops=[(0.0, (40, 56, 44)), (0.5, (56, 76, 54)), (0.8, (38, 54, 40)), (1.0, (20, 30, 24))],
        glowc=(168, 190, 130), dir="portrait"),
    "ziruo": dict(     # 自若：夜色的蓝绿，自在安然
        stops=[(0.0, (14, 22, 20)), (0.55, (24, 36, 30)), (1.0, (30, 42, 34))],
        glowc=(210, 205, 180), dir="portrait"),
}


def vine(img, x0, y0, length, seed):
    """垂蔓：一条弯线 + 小叶"""
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(24):
        t = i / 23
        pts.append((x0 + 18 * math.sin(t * 5 + seed) * (1 - t * 0.4), y0 + length * t))
    d.line(pts, fill=(26, 38, 30, 255), width=4)
    for i in range(2, 24, 4):
        px, py = pts[i]
        r = rnd.uniform(5, 9)
        d.ellipse([px - r, py - r * 0.6, px + r, py + r * 0.6], fill=(30, 44, 34, 255))


def portrait_series():
    out = os.path.join(GALLERY_DIR, "portrait")
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(101)
    poses = ["up", "out", "hold", None, "hold", "up", None, "out", "hold"]
    hats = [None, "wide", None, "cap", None, "wide", None, None, "cap"]

    for name, cfg in SERIES.items():
        for i in range(9):
            size = (800, 1200)
            img = vgrad(size, cfg["stops"]).convert("RGBA")
            gx = rnd.uniform(300, 500)
            gy = rnd.uniform(360, 520)
            glow(img, (gx, gy), rnd.uniform(200, 300), cfg["glowc"], alpha=80)
            hills(img, 950, 40, lerp(SIL, cfg["glowc"], 0.06), seed=i * 7 + 3)
            ground_y = 1080
            hills(img, ground_y - 30, 24, SIL, seed=i * 5 + 1)

            layer = Image.new("RGBA", size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            x = rnd.uniform(280, 520)
            h = rnd.uniform(330, 430)
            head = person(ld, x, ground_y - 40, h, lean=rnd.uniform(-0.4, 0.4),
                          arm=poses[i], hat=hats[i])
            if poses[i] == "hold" and name != "mansheng":
                lantern(img, int(head[0]), int(head[1] + h * 0.32))
            img.alpha_composite(layer)

            if name == "mansheng":   # 垂蔓从上方生长下来
                for v in range(rnd.randint(3, 5)):
                    vine(img, rnd.uniform(60, 740), 0, rnd.uniform(240, 520), seed=i * 13 + v)
                grass(img, 1050, (30, 44, 32), count=420, seed=i + 5)
            if name == "ziruo":
                stars(img, 300, ymax_ratio=0.6, seed=i + 9)
                grass(img, 1060, (24, 34, 28), count=380, seed=i + 6)
            if name == "xuzhang":
                mist_bands(img, 830, 950, alpha=26)
                grass(img, 1060, (52, 58, 36), count=380, seed=i + 7)

            save_jpg(add_grain(img.convert("RGB"), 4),
                     os.path.join(out, f"{name}-{i+1:02d}.jpg"), quality=84)


# ---------- 5. 人文（街巷烟火） ----------
def humanity():
    out = os.path.join(GALLERY_DIR, "humanity")
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(202)
    for i in range(6):
        size = (1200, 800)
        stops = [(0.0, (16, 24, 20)), (0.6, (26, 38, 30)), (1.0, (20, 30, 24))]
        img = vgrad(size, stops).convert("RGBA")
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        # 两侧建筑剪影
        bw1 = rnd.uniform(260, 380)
        ld.rectangle([0, rnd.uniform(180, 260), bw1, 800], fill=SIL2 + (255,))
        ld.rectangle([1200 - bw1 * 0.9, rnd.uniform(220, 300), 1200, 800], fill=SIL + (255,))
        # 暖窗几扇
        for w in range(rnd.randint(3, 5)):
            wx = rnd.uniform(40, bw1 - 60) if rnd.random() < 0.6 else rnd.uniform(1200 - bw1 * 0.9 + 30, 1140)
            wy = rnd.uniform(300, 560)
            ld.rectangle([wx, wy, wx + 34, wy + 48], fill=(214, 176, 108, rnd.randint(160, 235)))
        img.alpha_composite(layer)
        glow(img, (rnd.uniform(300, 900), 640), 160, GOLD, alpha=50)
        # 路灯
        lx = rnd.uniform(480, 720)
        ld2 = ImageDraw.Draw(img)
        ld2.line([(lx, 430), (lx, 800)], fill=SIL + (255,), width=10)
        lantern(img, int(lx), 420, r=16)
        # 行人一两个
        layer2 = Image.new("RGBA", size, (0, 0, 0, 0))
        l2 = ImageDraw.Draw(layer2)
        for p in range(rnd.randint(1, 2)):
            person(l2, rnd.uniform(380, 820), 800, rnd.uniform(150, 200),
                   lean=rnd.uniform(-0.5, 0.5), arm=rnd.choice([None, "hold"]),
                   hat=rnd.choice([None, "wide", "cap"]))
        img.alpha_composite(layer2)
        mist_bands(img, 620, 760, alpha=22)
        save_jpg(add_grain(img.convert("RGB"), 4),
                 os.path.join(out, f"renwen-{i+1:02d}.jpg"), quality=84)


# ---------- 6. 静物 ----------
def stilllife():
    out = os.path.join(GALLERY_DIR, "stilllife")
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(303)
    for i in range(5):
        size = (800, 1200)
        stops = [(0.0, (30, 42, 34)), (0.6, (38, 50, 40)), (1.0, (22, 32, 26))]
        img = vgrad(size, stops).convert("RGBA")
        d = ImageDraw.Draw(img)
        # 背后一扇窗的柔光
        wx0, wy0 = rnd.uniform(180, 320), rnd.uniform(140, 240)
        d.rectangle([wx0, wy0, wx0 + 240, wy0 + 360], fill=(206, 178, 118, 60))
        glow(img, (wx0 + 120, wy0 + 180), 260, GOLD, alpha=60)
        # 桌面线
        ty = 900
        d.rectangle([0, ty, 800, 1200], fill=(18, 26, 21, 255))
        kind = i % 5
        if kind == 0:      # 插枝花瓶
            d.polygon([(370, ty), (430, ty), (420, ty - 180), (380, ty - 180)], fill=SIL + (255,))
            for b in range(5):
                a = math.radians(-90 + (b - 2) * 22)
                ln = rnd.uniform(140, 240)
                ex, ey = 400 + ln * math.cos(a) * 0.7, (ty - 180) + ln * math.sin(a)
                d.line([(400, ty - 180), (ex, ey)], fill=SIL + (255,), width=4)
                d.ellipse([ex - 8, ey - 5, ex + 8, ey + 5], fill=SIL + (255,))
        elif kind == 1:    # 一盏茶杯，热气袅袅
            d.rectangle([350, ty - 90, 450, ty], fill=SIL + (255,))
            d.arc([440, ty - 70, 490, ty - 20], -90, 90, fill=SIL + (255,), width=10)
            for s in range(3):
                pts = []
                for k in range(20):
                    t = k / 19
                    pts.append((380 + s * 22 + 14 * math.sin(t * 4 + s), ty - 110 - t * 180))
                d.line(pts, fill=(150, 166, 148, 90), width=3)
        elif kind == 2:    # 一摞书
            for b in range(4):
                bw = rnd.uniform(180, 240)
                d.rectangle([400 - bw / 2, ty - 34 * (b + 1), 400 + bw / 2, ty - 34 * b],
                            fill=(SIL if b % 2 else SIL2) + (255,))
        elif kind == 3:    # 椅与影
            d.rectangle([300, ty - 260, 320, ty], fill=SIL + (255,))
            d.rectangle([440, ty - 260, 460, ty], fill=SIL + (255,))
            d.rectangle([290, ty - 300, 470, ty - 260], fill=SIL + (255,))
            d.rectangle([300, ty - 480, 320, ty - 300], fill=SIL + (255,))
        else:              # 小盆栽
            d.polygon([(360, ty), (440, ty), (424, ty - 110), (376, ty - 110)], fill=SIL + (255,))
            for b in range(6):
                a = math.radians(-90 + (b - 2.5) * 18)
                ln = rnd.uniform(90, 160)
                ex, ey = 400 + ln * math.cos(a) * 0.8, (ty - 110) + ln * math.sin(a)
                d.line([(400, ty - 110), (ex, ey)], fill=SIL + (255,), width=5)
                d.ellipse([ex - 10, ey - 6, ex + 10, ey + 6], fill=SIL + (255,))
        save_jpg(add_grain(img.convert("RGB"), 4),
                 os.path.join(out, f"jingwu-{i+1:02d}.jpg"), quality=84)


if __name__ == "__main__":
    hero_hd()
    girl_field()
    portrait_series()
    humanity()
    stilllife()
    print("ALL DONE")
