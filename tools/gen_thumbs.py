# -*- coding: utf-8 -*-
"""为 gallery 全部照片生成缩略图（长边 480px，质量 80）到 thumbs/ 镜像目录。
卡片用缩略图，灯箱仍加载原图。
色彩：带 ICC 的图先转换到 sRGB（Display P3 / Adobe RGB 不做转换会偏色）。"""
import io
import os

from PIL import Image, ImageCms

GALLERY = r"E:\3 workbuddy\portfolio\assets\img\gallery"
THUMBS = r"E:\3 workbuddy\portfolio\assets\img\thumbs"
MAX_SIDE = 480
SRGB = ImageCms.createProfile("sRGB")


def to_srgb(img):
    """带 ICC 的照片转换到 sRGB；无 ICC 或已是 sRGB 的按原样。"""
    icc = img.info.get("icc_profile")
    if icc:
        try:
            src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            if "sRGB" not in str(src_profile.profileDescription):
                return ImageCms.profileToProfile(img, src_profile, SRGB, outputMode="RGB")
        except Exception:
            pass
    return img.convert("RGB")


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
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            img = Image.open(src)
            img = to_srgb(img)
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
