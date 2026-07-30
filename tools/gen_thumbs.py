# -*- coding: utf-8 -*-
"""为 gallery 全部照片生成缩略图（长边 480px，质量 80）到 thumbs/ 镜像目录。
卡片用缩略图，灯箱仍加载原图。"""
import os

from PIL import Image

GALLERY = r"E:\3 workbuddy\portfolio\assets\img\gallery"
THUMBS = r"E:\3 workbuddy\portfolio\assets\img\thumbs"
MAX_SIDE = 480


def main():
    count = 0
    total_kb = 0
    for dirpath, _dirs, files in os.walk(GALLERY):
        for f in files:
            if not f.lower().endswith((".jpg", ".jpeg")):
                continue
            src = os.path.join(dirpath, f)
            rel = os.path.relpath(src, GALLERY)
            dst = os.path.join(THUMBS, rel)
            if os.path.isfile(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            img = Image.open(src)
            w, h = img.size
            scale = MAX_SIDE / max(w, h)
            if scale < 1:
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            img.convert("RGB").save(dst, "JPEG", quality=80, optimize=True)
            count += 1
            total_kb += os.path.getsize(dst) // 1024
    print("缩略图 %d 张，共 %d KB" % (count, total_kb))


if __name__ == "__main__":
    main()
