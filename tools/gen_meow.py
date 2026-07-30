# -*- coding: utf-8 -*-
"""喵星人栏：3 张占位图（田野上的猫咪剪影，预留位置，用户同名覆盖即换真照片）。"""
import math
import os
import random

from PIL import Image, ImageDraw

from generate_assets import (vgrad, glow, hills, stars, mist_bands, grass,
                             add_grain, save_jpg, lerp, GOLD, GALLERY_DIR)
from generate_more import SIL, SIL2

W, H = 900, 1350


def cat(d, x, ground, h, pose="sit"):
    """猫的剪影。pose: sit 坐 / stand 站 / lie 趴。"""
    if pose == "sit":
        # 身体（水滴形，下宽上窄）
        d.ellipse([x - h * 0.20, ground - h * 0.52, x + h * 0.20, ground], fill=SIL + (255,))
        # 头
        hr = h * 0.13
        hy = ground - h * 0.58
        d.ellipse([x - hr, hy - hr, x + hr, hy + hr], fill=SIL + (255,))
        # 耳朵
        d.polygon([(x - hr * 0.9, hy - hr * 0.5), (x - hr * 0.55, hy - hr * 1.45),
                   (x - hr * 0.15, hy - hr * 0.75)], fill=SIL + (255,))
        d.polygon([(x + hr * 0.9, hy - hr * 0.5), (x + hr * 0.55, hy - hr * 1.45),
                   (x + hr * 0.15, hy - hr * 0.75)], fill=SIL + (255,))
        # 尾巴绕到身前
        d.arc([x + h * 0.02, ground - h * 0.30, x + h * 0.42, ground + h * 0.06],
              90, 300, fill=SIL + (255,), width=int(h * 0.055))
    elif pose == "stand":
        # 身体（长椭圆）
        d.ellipse([x - h * 0.32, ground - h * 0.42, x + h * 0.22, ground - h * 0.12], fill=SIL + (255,))
        # 腿
        for lx in [-0.24, -0.12, 0.08, 0.18]:
            d.line([(x + h * lx, ground - h * 0.22), (x + h * lx, ground)],
                   fill=SIL + (255,), width=int(h * 0.04))
        # 头
        hr = h * 0.115
        hx, hy = x + h * 0.26, ground - h * 0.46
        d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=SIL + (255,))
        d.polygon([(hx - hr * 0.9, hy - hr * 0.5), (hx - hr * 0.55, hy - hr * 1.45),
                   (hx - hr * 0.15, hy - hr * 0.75)], fill=SIL + (255,))
        d.polygon([(hx + hr * 0.9, hy - hr * 0.5), (hx + hr * 0.55, hy - hr * 1.45),
                   (hx + hr * 0.15, hy - hr * 0.75)], fill=SIL + (255,))
        # 尾巴上翘
        d.arc([x - h * 0.48, ground - h * 0.72, x - h * 0.16, ground - h * 0.2],
              270, 90, fill=SIL + (255,), width=int(h * 0.05))
    else:  # lie 趴着
        d.ellipse([x - h * 0.34, ground - h * 0.26, x + h * 0.28, ground], fill=SIL + (255,))
        hr = h * 0.12
        hx, hy = x + h * 0.28, ground - h * 0.28
        d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=SIL + (255,))
        d.polygon([(hx - hr * 0.9, hy - hr * 0.5), (hx - hr * 0.55, hy - hr * 1.45),
                   (hx - hr * 0.15, hy - hr * 0.75)], fill=SIL + (255,))
        d.polygon([(hx + hr * 0.9, hy - hr * 0.5), (hx + hr * 0.55, hy - hr * 1.45),
                   (hx + hr * 0.15, hy - hr * 0.75)], fill=SIL + (255,))
        # 尾巴盘在身侧
        d.arc([x - h * 0.40, ground - h * 0.22, x - h * 0.06, ground + h * 0.04],
              60, 260, fill=SIL + (255,), width=int(h * 0.05))


def main():
    out = os.path.join(GALLERY_DIR, "meow")
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(111)
    poses = ["sit", "stand", "lie"]
    for i in range(3):
        img = vgrad((W, H), [(0.0, (13, 20, 17)), (0.55, (26, 40, 32)), (1.0, (18, 28, 23))]).convert("RGBA")
        glow(img, (rnd.uniform(320, 580), rnd.uniform(380, 520)), 260, GOLD, alpha=65)
        stars(img, 200, ymax_ratio=0.5, gold_ratio=0.12, seed=i * 7 + 11)
        hills(img, 940, 40, SIL2, seed=i * 5 + 3)
        hills(img, 1070, 26, SIL, seed=i * 3 + 6)
        mist_bands(img, 860, 1010, alpha=24)
        d = ImageDraw.Draw(img)
        cat(d, W / 2 + rnd.uniform(-40, 40), 1090, 430, pose=poses[i])
        grass(img, 1110, (42, 56, 40), count=420, seed=i + 21)
        save_jpg(add_grain(img.convert("RGB"), 4),
                 os.path.join(out, "meow-%02d.jpg" % (i + 1)), quality=84)
    print("meow done")


if __name__ == "__main__":
    main()
