# -*- coding: utf-8 -*-
"""首页「进入我的宇宙」：两个小星系入口图（暖金=摄影，青绿=AI视频）。"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

from generate_assets import vgrad, glow, stars, add_grain, save_jpg, IMG_DIR

SIZE = 880


def galaxy(path, arm_color, core_color, seed):
    rnd = random.Random(seed)
    # 底色与页面背景 #0e1613 完全一致，边缘自然融入页面
    img = vgrad((SIZE, SIZE), [(0.0, (14, 22, 19)), (1.0, (14, 22, 19))]).convert("RGBA")
    cx = cy = SIZE / 2

    # 背景星点（稀疏，靠近星系）
    stars(img, 130, ymax_ratio=1.0, gold_ratio=0.12, seed=seed + 1)

    # 星系核心
    glow(img, (cx, cy), 90, core_color, alpha=150)
    glow(img, (cx, cy), 34, (248, 242, 220), alpha=150)

    # 旋臂：对数螺旋线上的星尘点
    arms = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arms)
    for arm in range(2):
        a0 = arm * math.pi
        for i in range(5600):
            t = rnd.random() ** 0.55         # 越往外越稀
            ang = a0 + t * 4.9
            r = 20 + t * 330
            # 加噪声让旋臂有厚度
            r += rnd.gauss(0, 7 + t * 22)
            ang += rnd.gauss(0, 0.04 + t * 0.08)
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang) * 0.58   # 压扁成椭圆视角
            b = int(210 * (1 - t * 0.7) * rnd.uniform(0.35, 1.0))
            sz = rnd.uniform(0.4, 1.2)
            col = tuple(min(255, int(c * (0.55 + 0.45 * (1 - t)))) for c in arm_color)
            ad.ellipse([x - sz, y - sz, x + sz, y + sz], fill=col + (max(0, min(235, b)),))
    arms = arms.filter(ImageFilter.GaussianBlur(1.1))
    img.alpha_composite(arms)

    # 旋臂上撒少量亮星
    bright = ImageDraw.Draw(img)
    for _ in range(60):
        t = rnd.random()
        ang = rnd.choice([0, math.pi]) + t * 4.9 + rnd.gauss(0, 0.1)
        r = 24 + t * 320 + rnd.gauss(0, 14)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang) * 0.58
        s = rnd.uniform(0.9, 2.2)
        bright.ellipse([x - s, y - s, x + s, y + s],
                       fill=(246, 240, 220, rnd.randint(120, 220)))

    # 外圈淡淡光晕收边
    glow(img, (cx, cy), 420, arm_color, alpha=22)
    save_jpg(add_grain(img.convert("RGB"), 3), path, quality=90)
    print("saved:", path)


if __name__ == "__main__":
    galaxy(os.path.join(IMG_DIR, "galaxy-photo.jpg"), (222, 188, 120), (232, 206, 140), 88)   # 暖金
    galaxy(os.path.join(IMG_DIR, "galaxy-dream.jpg"), (150, 190, 158), (188, 214, 190), 99)   # 青绿
