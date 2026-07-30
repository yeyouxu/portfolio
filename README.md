# 野有叙 — 摄影师个人网站

温柔、安静，像走进田野。深绿低饱和 + 暖金点缀，诗集式排版的画册型个人网站。

## 页面

| 页面 | 文件 | 内容 |
|------|------|------|
| 首页 | `index.html` | 星空大图首屏（鼠标悬停点亮星星、连成星座）、序、精选作品带（视差滚动） |
| 作品 | `works.html` | 摄影 / AI 视频双分类，可筛选，点击打开灯箱（图片放大查看、视频播放） |
| 关于我 | `about.html` | 肖像、自述、视差装饰带 |
| 联系 | `contact.html` | 联系方式 + 留言板 |

## 设计说明（对照需求）

- **色彩**：深绿 `#0e1613`~`#48604f`（低饱和），点缀暖金 `#c8a96b`，整体柔和低对比
- **排版**：标题衬线体（Noto Serif SC / 宋体回退），正文黑体（Noto Sans SC）；字距 0.06–0.34em，行距 2.1，诗集感
- **交互**：图片悬停放大、点击平滑过渡、视差滚动、星空悬停点亮
- **动效**：0.5s 柔和过渡、从下往上淡入、仅关键位置动（克制）；支持 `prefers-reduced-motion`
- **实用**：响应式（手机/桌面）、图片原生懒加载 `loading="lazy"`、纯静态零依赖

## 替换为你自己的作品

1. 照片放入 `assets/img/gallery/`，视频放入 `assets/videos/`
2. 打开 `assets/js/works-data.js`，修改条目（`type: "photo"` 或 `"video"`）即可
3. 关于页肖像替换 `assets/img/portrait.jpg`，联系方式在 `contact.html` 中修改

占位素材由 `tools/generate_assets.py` 本地生成，不需要可整个删除。

## 部署到 GitHub Pages

```bash
cd portfolio
git init
git add .
git commit -m "野有叙：个人摄影网站"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

然后到仓库页面：**Settings → Pages → Source 选 `main` 分支 / 根目录 → Save**。
几分钟后访问 `https://<你的用户名>.github.io/<仓库名>/`。

> 若仓库名是 `<你的用户名>.github.io`，则直接访问该地址即可。
> 项目已包含 `.nojekyll`，确保下划线目录等资源不被 Jekyll 忽略。

## 留言板：从"本地版"升级为"所有人可见"

当前留言板用 `localStorage` 实现（留言只存在访客自己的浏览器）。GitHub Pages 是纯静态托管，没有数据库，推荐用 [Giscus](https://giscus.app/zh-CN)（基于 GitHub Discussions，免费）：

1. 仓库设为 **Public**，并在仓库 Settings → Features 勾选 **Discussions**
2. 安装 Giscus App：<https://github.com/apps/giscus>（授权该仓库）
3. 打开 <https://giscus.app/zh-CN> 填好仓库，复制生成的 `<script>` 代码
4. 粘贴到 `contact.html` 的 `#gbList` 位置（替换或并列均可），主题可选 `dark_dimmed` 搭配本站配色

## 本地预览

```bash
# 任选其一
python -m http.server 8000
npx serve .
```

打开 <http://localhost:8000>。
