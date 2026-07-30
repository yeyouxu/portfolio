# -*- coding: utf-8 -*-
"""关于我页照片：女孩背影（长发、长裙、颈挂相机）+ 身旁一株有韧性的小草。
呼应文案「一株匍匐在地、很有韧性的草」与「我出门喜欢带上我的相机」。"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

from generate_assets import (vgrad, glow, hills, stars, mist_bands, grass,
                             add_grain, save_jpg, lerp, GOLD, IMG_DIR)
from generate_more import SIL, SIL2

W, H = 900, 1125


def girl(d, x, ground, h):
    """女孩背影剪影：长发、A 字长裙、胸前挂相机。返回头部中心。"""
    head_r = h * 0.085
    head_y = ground - h + head_r * 1.4
    # 长裙（A 字，从腰到地）
    waist_y = ground - h * 0.52
    d.polygon([(x - h * 0.10, waist_y), (x + h * 0.10, waist_y),
               (x + h * 0.20, ground), (x - h * 0.20, ground)], fill=SIL + (255,))
    # 上身（肩到腰）
    d.polygon([(x - h * 0.115, waist_y - h * 0.24), (x + h * 0.115, waist_y - h * 0.24),
               (x + h * 0.10, waist_y), (x - h * 0.10, waist_y)], fill=SIL + (255,))
    # 手臂自然垂落
    d.line([(x - h * 0.10, waist_y - h * 0.20), (x - h * 0.16, waist_y + h * 0.10)],
           fill=SIL + (255,), width=int(h * 0.045))
    d.line([(x + h * 0.10, waist_y - h * 0.20), (x + h * 0.16, waist_y + h * 0.10)],
           fill=SIL + (255,), width=int(h * 0.045))
    # 头
    d.ellipse([x - head_r, head_y - head_r, x + head_r, head_y + head_r], fill=SIL + (255,))
    # 脖子（连接头与上身，让头发与肩之间透出间隙）
    neck_y = waist_y - h * 0.24          # 肩线高度
    d.rectangle([x - head_r * 0.32, head_y + head_r * 0.5,
                 x + head_r * 0.32, neck_y + h * 0.012], fill=SIL + (255,))
    # 长发：头顶垂至肩上方，发尾收窄于肩膀内侧——头发与肩之间留出间隙
    hair_end_y = neck_y + h * 0.02
    d.polygon([(x - head_r * 0.95, head_y - head_r * 0.4),
               (x + head_r * 0.95, head_y - head_r * 0.4),
               (x + head_r * 1.02, head_y + head_r * 1.1),    # 耳侧
               (x + head_r * 0.82, hair_end_y),                # 右发尾（肩内侧、肩线上方）
               (x + head_r * 0.42, hair_end_y + h * 0.012),
               (x - head_r * 0.42, hair_end_y + h * 0.012),
               (x - head_r * 0.82, hair_end_y),
               (x - head_r * 1.02, head_y + head_r * 1.1)], fill=SIL + (255,))
    # 相机：右手侧提，机身微亮于裙色 + 顶边一道金色反光（背影中可辨）
    hand_x, hand_y = x + h * 0.16, waist_y + h * 0.10
    cam_y = hand_y + h * 0.075
    d.line([(hand_x, hand_y), (hand_x + h * 0.005, cam_y - h * 0.03)],
           fill=SIL2 + (255,), width=3)
    d.rectangle([hand_x - h * 0.035, cam_y - h * 0.028, hand_x + h * 0.045, cam_y + h * 0.028],
                fill=(20, 28, 23, 255))
    d.ellipse([hand_x - h * 0.002, cam_y - h * 0.015, hand_x + h * 0.03, cam_y + h * 0.015],
              fill=(16, 24, 19, 255))
    d.line([(hand_x - h * 0.035, cam_y - h * 0.028), (hand_x + h * 0.045, cam_y - h * 0.028)],
           fill=(198, 168, 106, 200), width=2)
    return x, head_y


def blade(d, x, y, length, angle, width, color, glow_color=None):
    """一片草叶：从 (x,y) 沿 angle 方向生长 length，带弧度的细长叶形。"""
    steps = 12
    left, right = [], []
    bend = math.radians(angle)
    curve = 0.35                      # 弯曲程度
    for i in range(steps + 1):
        t = i / steps
        ang = bend + curve * t * (1 if angle < 0 else -1) * 0.6
        r = length * t
        cx = x + r * math.sin(ang)
        cy = y - r * math.cos(ang)
        w = width * (1 - t) * (0.35 + 0.65 * (1 - t)) + 0.6
        nx = math.cos(ang) * w
        ny = math.sin(ang) * w
        left.append((cx - nx, cy - ny))
        right.append((cx + nx, cy + ny))
    d.polygon(left + right[::-1], fill=color + (255,))
    # 叶尖一点金色逆光
    tip = left[-1]
    d.ellipse([tip[0] - 2.5, tip[1] - 2.5, tip[0] + 2.5, tip[1] + 2.5],
              fill=(214, 186, 120, 200))


def main():
    img = vgrad((W, H), [(0.0, (11, 18, 15)), (0.55, (22, 34, 27)), (1.0, (16, 25, 20))]).convert("RGBA")
    # 天将亮未亮的微光（左后方）
    glow(img, (300, 420), 300, GOLD, alpha=60)
    stars(img, 140, ymax_ratio=0.35, gold_ratio=0.1, seed=71)

    # 远山与地
    hills(img, 830, 46, lerp(SIL, GOLD, 0.05), seed=72)
    hills(img, 950, 28, SIL, seed=73)
    mist_bands(img, 780, 930, alpha=28)

    d = ImageDraw.Draw(img)
    ground = 1030

    # 女孩（站在画面左中）
    gx, ground_y = 400, ground
    girl(d, gx, ground_y, 560)

    # 一株小草（女孩右前方，逆光金边）
    grass_x, grass_y = 585, ground + 6
    d.ellipse([grass_x - 26, grass_y - 4, grass_x + 26, grass_y + 6], fill=SIL2 + (255,))
    for length, angle, width in [(150, -22, 7), (185, -8, 8), (170, 6, 8),
                                 (140, 20, 7), (110, -32, 6), (120, 34, 6), (95, 0, 6)]:
        blade(d, grass_x, grass_y, length, angle, width, (24, 38, 28))
    # 小草根部微光
    glow(img, (grass_x, grass_y - 60), 90, GOLD, alpha=20)

    # 前景草地点缀
    grass(img, 1040, (40, 54, 38), count=360, seed=74)

    save_jpg(add_grain(img.convert("RGB"), 4),
             os.path.join(IMG_DIR, "portrait.jpg"), quality=88)
    print("saved: portrait.jpg")


if __name__ == "__main__":
    main()
