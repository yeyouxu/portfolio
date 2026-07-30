# -*- coding: utf-8 -*-
"""精选独立化：把精选占位图做成 featured/ 目录下的独立文件（复制自生成的小占位图，
不使用用户真照片，避免浪费空间）。用户以后在 GitHub 网页同名覆盖这些文件即可完成"单独挑选"。"""
import os
import shutil

GALLERY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "img", "gallery")
GALLERY = os.path.normpath(GALLERY)

# 每组 9 张的复制源（只用 <600KB 的生成占位图）
SOURCES = {
    "portrait":  ["portrait/weixi-%02d.jpg" % i for i in range(1, 10)],
    "landscape": ["landscape/%s/%s-01.jpg" % (s, s) for s in
                  ["mingxiaoling", "xizang", "yuanmu", "liudong", "wuxiang",
                   "feidi", "qingdao", "yuese", "qixiashan"]],
    "humanity":  ["humanity/renwen-%02d.jpg" % ((i % 3) + 4) for i in range(9)],
    "stilllife": ["stilllife/ziyou/ziyou-%02d.jpg" % (i + 1) for i in range(6)] +
                 ["stilllife/wenrou/wenrou-%02d.jpg" % (i + 1) for i in range(3)],
}


def main():
    out = os.path.join(GALLERY, "featured")
    os.makedirs(out, exist_ok=True)
    for group, srcs in SOURCES.items():
        assert len(srcs) == 9, group
        for i, rel in enumerate(srcs):
            src = os.path.join(GALLERY, rel)
            dst = os.path.join(out, "%s-%02d.jpg" % (group, i + 1))
            # 保护：若目标已是大文件（用户已换成真照片），跳过
            if os.path.exists(dst) and os.path.getsize(dst) > 600 * 1024:
                print("skip (用户真照片):", dst)
                continue
            shutil.copyfile(src, dst)
            print("ok:", group, i + 1)
    print("featured done")


if __name__ == "__main__":
    main()
