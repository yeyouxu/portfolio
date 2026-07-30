/* 作品页：摄影（精选/人像/风景/人文/静物/全部）+ AI 视频
   精选 = 独立挑选（cat:featured），四类各 9 张 + 链接卡；
   人像/风景/静物 = 系列行横滑（左右箭头 + 可滑时底部滚动条）；
   卷耳含 11 个子组；目录为可折叠树（三级默认折叠）；
   ?view=video 直达 AI 视频栏；灯箱按当前组翻页。 */
(function () {
  "use strict";

  var grid = document.getElementById("galleryGrid");
  if (!grid || !window.WORKS) return;

  var PLAY_SVG = '<svg viewBox="0 0 10 12"><path d="M0 0 L10 6 L0 12 Z"/></svg>';
  var tocEl = document.getElementById("tocNav");
  var layoutEl = document.querySelector(".works-layout");
  var tocTree = [];     // 目录树 [{text,id,depth,children:[]}]
  var tocIO = null;

  /* ---------- 工具 ---------- */
  function catName(key) {
    var c = window.CATS.find(function (x) { return x.key === key; });
    return c ? c.name : key;
  }
  function itemsOf(cat) {
    return window.WORKS.filter(function (w) { return w.cat === cat; });
  }
  function seriesOf(cat, key) {
    return window.WORKS.filter(function (w) { return w.cat === cat && w.series === key; });
  }
  function subOf(cat, key, sub) {
    return window.WORKS.filter(function (w) {
      return w.cat === cat && w.series === key && w.sub === sub;
    });
  }

  /* ---------- 卡片 ---------- */
  function makeCard(w, list, idx, inRow) {
    var card = document.createElement("figure");
    card.className = "work-card" + (w.wide ? " wide" : "") + (inRow ? " row-card" : "");
    card.setAttribute("data-cat", w.cat);

    var media = document.createElement("img");
    media.src = w.thumb || w.src;   /* 卡片用缩略图，灯箱仍加载原图 */
    media.alt = w.title;
    media.loading = "lazy";
    media.decoding = "async";
    media.draggable = false;
    media.addEventListener("load", function () {
      var nw = media.naturalWidth, nh = media.naturalHeight;
      if (inRow) {
        card.style.width = (nw / nh * card.parentElement.clientHeight) + "px";
        requestAnimationFrame(updateRowUI);
      } else if (nw > nh) {
        card.classList.add("wide");
      }
    });
    card.appendChild(media);

    if (w.type === "video") {
      var badge = document.createElement("span");
      badge.className = "badge-video";
      badge.innerHTML = PLAY_SVG + "摄影+AI融合视频";
      card.appendChild(badge);
    }

    var veil = document.createElement("div");
    veil.className = "card-veil";
    var info = document.createElement("figcaption");
    info.className = "card-info";
    info.innerHTML = "<h3>" + w.title + "</h3><p>" + w.desc + "</p>";
    card.appendChild(veil);
    card.appendChild(info);

    card.addEventListener("click", function () { openAt(list, idx); });
    return card;
  }

  function makeMoreCard(cat) {
    var card = document.createElement("figure");
    card.className = "work-card more-card";
    card.innerHTML = '<div class="more-inner"><span>更多' + catName(cat) +
      '作品</span><i>→</i></div>';
    card.addEventListener("click", function () { setSub(cat, true); });
    return card;
  }

  /* ---------- 组头 + 目录树收集 ---------- */
  var curL1 = null, curL2 = null;   // 当前目录树节点指针

  function makeHeader(text, depth, poem) {
    var h = document.createElement("div");
    h.className = "series-header" + (depth === 2 ? " sub" : depth === 3 ? " sub3" : "");
    var id = "group-" + tocCount++;
    h.id = id;
    var html = "<span>" + text + "</span>";
    if (poem) html += '<em class="s-poem">' + poem + "</em>";
    h.innerHTML = html;

    var node = { text: text, id: id, depth: depth, children: [] };
    if (depth === 1) { tocTree.push(node); curL1 = node; curL2 = null; }
    else if (depth === 2 && curL1) { curL1.children.push(node); curL2 = node; }
    else if (depth === 3 && curL2) { curL2.children.push(node); }
    return h;
  }

  /* ---------- 目录树渲染（可折叠；三级默认折叠） ---------- */
  function buildToc() {
    if (!tocEl) return;
    if (tocIO) { tocIO.disconnect(); tocIO = null; }
    tocEl.innerHTML = "";
    if (!tocTree.length) {
      tocEl.classList.remove("show");
      if (layoutEl) layoutEl.classList.add("no-toc");
      return;
    }
    if (layoutEl) layoutEl.classList.remove("no-toc");

    var title = document.createElement("p");
    title.className = "toc-title";
    title.textContent = "目 录";
    tocEl.appendChild(title);

    function makeNode(node) {
      var wrap = document.createElement("div");
      wrap.className = "toc-node depth-" + node.depth;

      var row = document.createElement("div");
      row.className = "toc-row";

      var fold = document.createElement("button");
      fold.className = "toc-fold";
      fold.setAttribute("aria-label", "折叠/展开");
      if (node.children.length) {
        // 子级深度 >=3（即三级）默认折叠
        var collapsed = node.children[0].depth >= 3;
        fold.textContent = collapsed ? "▸" : "▾";
        fold.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          collapsed = !collapsed;
          fold.textContent = collapsed ? "▸" : "▾";
          kids.classList.toggle("collapsed", collapsed);
        });
      } else {
        fold.classList.add("empty");
      }
      row.appendChild(fold);

      var a = document.createElement("a");
      a.href = "#" + node.id;
      a.className = "toc-link" + (node.depth === 2 ? " sub" : node.depth === 3 ? " sub3" : "");
      a.textContent = node.text;
      a.setAttribute("data-target", node.id);
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var el = document.getElementById(node.id);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      row.appendChild(a);
      wrap.appendChild(row);

      var kids = document.createElement("div");
      kids.className = "toc-children";
      if (node.children.length && node.children[0].depth >= 3) {
        kids.classList.add("collapsed");   // 三级默认折叠
      }
      node.children.forEach(function (c) { kids.appendChild(makeNode(c)); });
      wrap.appendChild(kids);
      return wrap;
    }

    tocTree.forEach(function (n) { tocEl.appendChild(makeNode(n)); });
    tocEl.classList.add("show");

    // 滚动高亮
    var links = {};
    tocEl.querySelectorAll(".toc-link").forEach(function (l) {
      links[l.getAttribute("data-target")] = l;
    });
    var first = true;
    tocIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        tocEl.querySelectorAll(".toc-link").forEach(function (l) { l.classList.remove("active"); });
        var link = links[en.target.id];
        if (link) link.classList.add("active");
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(links).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) tocIO.observe(el);
    });
    // 默认高亮第一个
    var firstId = Object.keys(links)[0];
    if (firstId && links[firstId]) links[firstId].classList.add("active");
  }

  /* ---------- 系列横滑行（左右箭头 + 共N张 + 可滑时滚动条） ---------- */
  function updateRowUI() {
    document.querySelectorAll(".row-track").forEach(function (track) {
      var wrap = track.parentElement;
      var prev = wrap.querySelector(".row-prev");
      var next = wrap.querySelector(".row-next");
      var count = wrap.querySelector(".row-count");
      var canScroll = track.scrollWidth > track.clientWidth + 12;
      track.classList.toggle("scrollable", canScroll);
      if (prev) prev.classList.toggle("gone", !canScroll || track.scrollLeft <= 12);
      if (next) next.classList.toggle("gone",
        !canScroll || track.scrollLeft + track.clientWidth >= track.scrollWidth - 12);
      if (count) count.classList.toggle("gone", !canScroll);
    });
  }

  function makeRow(items) {
    var wrap = document.createElement("div");
    wrap.className = "row-wrap";
    var track = document.createElement("div");
    track.className = "row-track";
    items.forEach(function (w, i) { track.appendChild(makeCard(w, items, i, true)); });
    wrap.appendChild(track);

    var prev = document.createElement("button");
    prev.className = "row-prev gone";
    prev.setAttribute("aria-label", "向前翻看");
    prev.innerHTML = "‹";
    prev.addEventListener("click", function () {
      track.scrollBy({ left: -track.clientWidth * 0.8, behavior: "smooth" });
    });
    wrap.appendChild(prev);

    // 右滑箭头 + 「共 N 张」（一组滑不完时才显示）
    var nextBox = document.createElement("div");
    nextBox.className = "row-next-box";
    var count = document.createElement("span");
    count.className = "row-count gone";
    count.textContent = "共 " + items.length + " 张";
    nextBox.appendChild(count);
    var next = document.createElement("button");
    next.className = "row-next gone";
    next.setAttribute("aria-label", "向后翻看");
    next.innerHTML = "›";
    next.addEventListener("click", function () {
      track.scrollBy({ left: track.clientWidth * 0.8, behavior: "smooth" });
    });
    nextBox.appendChild(next);
    wrap.appendChild(nextBox);

    track.addEventListener("scroll", updateRowUI);
    return wrap;
  }

  function makeSeriesBlock(cat, sDef, baseDepth) {
    var items = seriesOf(cat, sDef.key);
    var children = sDef.children || [];
    if (!items.length && !children.length) return null;

    var block = document.createElement("div");
    block.className = "series-block";
    // depth：分类栏里系列为一级（卷耳子组二级、目录默认展开）；
    //        全部栏里系列为二级（子组三级、目录默认折叠）
    block.appendChild(makeHeader(sDef.key, baseDepth, sDef.sub || ""));

    if (children.length) {
      // 含子组的系列（卷耳）：每个子组一行
      children.forEach(function (subName) {
        var subItems = subOf(cat, sDef.key, subName);
        if (!subItems.length) return;
        var subBlock = document.createElement("div");
        subBlock.className = "series-block sub-block";
        subBlock.appendChild(makeHeader(subName, baseDepth + 1));
        subBlock.appendChild(makeRow(subItems));
        block.appendChild(subBlock);
      });
    } else {
      block.appendChild(makeRow(items));
    }
    return block;
  }

  /* ---------- 各视图 ---------- */
  function renderFeatured() {
    window.CATS.forEach(function (c) {
      var feats = window.WORKS.filter(function (w) {
        return w.cat === "featured" && w.group === c.key;
      }).slice(0, 9);
      if (!feats.length) return;
      grid.appendChild(makeHeader("精选" + c.name, 1));
      var sub = document.createElement("div");
      sub.className = "gallery";
      feats.forEach(function (w, i) { sub.appendChild(makeCard(w, feats, i)); });
      sub.appendChild(makeMoreCard(c.key));
      grid.appendChild(sub);
    });
  }

  function renderSeriesCat(cat, withCatHeader) {
    var baseDepth = withCatHeader ? 2 : 1;   // 全部栏含分类大标题，系列降为二级
    if (withCatHeader) grid.appendChild(makeHeader(catName(cat), 1));
    (window.SERIES[cat] || []).forEach(function (sDef) {
      var block = makeSeriesBlock(cat, sDef, baseDepth);
      if (block) grid.appendChild(block);
    });
  }

  function renderGridCat(cat, withHeader) {
    var items = itemsOf(cat);
    if (withHeader !== false) grid.appendChild(makeHeader(catName(cat), 1));
    var sub = document.createElement("div");
    sub.className = "gallery";
    items.forEach(function (w, i) { sub.appendChild(makeCard(w, items, i)); });
    grid.appendChild(sub);
  }

  function renderAll() {
    window.CATS.forEach(function (c) {
      if (window.SERIES[c.key]) {
        renderSeriesCat(c.key, true);
      } else {
        renderGridCat(c.key);
      }
    });
  }

  function renderVideo() {
    var items = window.WORKS.filter(function (w) { return w.type === "video"; });
    var sub = document.createElement("div");
    sub.className = "gallery";
    items.forEach(function (w, i) { sub.appendChild(makeCard(w, items, i)); });
    grid.appendChild(sub);
  }

  var tocCount = 0;
  function render() {
    grid.innerHTML = "";
    tocTree = [];
    tocCount = 0;
    if (state.main === "video") {
      renderVideo();
    } else if (state.sub === "featured") {
      renderFeatured();
    } else if (state.sub === "all") {
      renderAll();
    } else if (window.SERIES[state.sub]) {
      renderSeriesCat(state.sub);
    } else {
      renderGridCat(state.sub);
    }
    buildToc();
    requestAnimationFrame(updateRowUI);
  }

  /* ---------- 筛选栏 ---------- */
  var bar = document.getElementById("filterBar");
  var subBar = document.getElementById("subFilterBar");
  var state = { main: "photo", sub: "featured" };

  function syncBar() {
    if (bar) {
      bar.querySelectorAll(".filter-btn").forEach(function (b) {
        b.classList.toggle("active", b.getAttribute("data-filter") === state.main);
      });
    }
    if (subBar) {
      subBar.classList.toggle("show", state.main === "photo");
      subBar.querySelectorAll(".filter-btn").forEach(function (b) {
        b.classList.toggle("active", b.getAttribute("data-filter") === state.sub);
      });
    }
  }

  /* 切换子栏目；toTop=true 时页面滚动条回到最上方（点「更多作品」） */
  function setSub(sub, toTop) {
    state.main = "photo";
    state.sub = sub;
    syncBar();
    render();
    if (toTop) {
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      var sec = document.querySelector(".works-layout");
      if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  if (bar) {
    bar.addEventListener("click", function (e) {
      var btn = e.target.closest(".filter-btn");
      if (!btn) return;
      state.main = btn.getAttribute("data-filter");
      if (state.main === "photo" && !state.sub) state.sub = "featured";
      syncBar();
      render();
    });
  }

  if (subBar) {
    subBar.addEventListener("click", function (e) {
      var btn = e.target.closest(".filter-btn");
      if (!btn) return;
      state.sub = btn.getAttribute("data-filter");
      syncBar();
      render();
    });
  }

  var q = new URLSearchParams(location.search).get("view");
  if (q === "video") { state.main = "video"; }

  window.addEventListener("resize", updateRowUI);

  /* ---------- 灯箱 ---------- */
  var lb, curList = [], cur = -1;

  function buildLightbox() {
    lb = document.createElement("div");
    lb.className = "lightbox";
    lb.innerHTML =
      '<button class="lightbox-close" aria-label="关闭">×</button>' +
      '<button class="lightbox-nav prev" aria-label="上一张">‹</button>' +
      '<div class="lightbox-box"></div>' +
      '<button class="lightbox-nav next" aria-label="下一张">›</button>';
    document.body.appendChild(lb);
    lb.querySelector(".lightbox-close").addEventListener("click", close);
    lb.querySelector(".prev").addEventListener("click", function (e) { e.stopPropagation(); step(-1); });
    lb.querySelector(".next").addEventListener("click", function (e) { e.stopPropagation(); step(1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (cur < 0) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    });
  }

  function show() {
    var w = curList[cur];
    if (!w) return;
    var box = lb.querySelector(".lightbox-box");
    box.innerHTML = "";
    var el;
    if (w.type === "video") {
      el = document.createElement("video");
      el.src = w.video;
      el.controls = true;
      el.setAttribute("controlsList", "nodownload");
      el.setAttribute("disablePictureInPicture", "");
      el.autoplay = true;
      el.loop = true;
      el.muted = false;          // 默认打开声音
      el.playsInline = true;
      // 浏览器若拦截有声自动播放，回退为静音播放（用户点音量键即可开声）
      var tryPlay = function () {
        var p = el.play();
        if (p && p.catch) {
          p.catch(function () {
            el.muted = true;
            el.play().catch(function () {});
          });
        }
      };
      if (el.readyState >= 2) { tryPlay(); }
      else { el.addEventListener("canplay", tryPlay, { once: true }); }
    } else {
      el = document.createElement("img");
      el.src = w.src;
      el.alt = w.title;
      el.draggable = false;
    }
    box.appendChild(el);
    var cap = document.createElement("p");
    cap.className = "lightbox-caption";
    cap.textContent = (w.series ? w.series + " " : "") +
      (w.sub ? w.sub + " · " : "") + w.title + (w.desc ? " — " + w.desc : "");
    box.appendChild(cap);
  }

  function openAt(list, i) {
    if (!lb) buildLightbox();
    curList = list;
    cur = i;
    show();
    lb.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function step(d) {
    if (!curList.length) return;
    var old = lb.querySelector("video");
    if (old) old.pause();
    cur = (cur + d + curList.length) % curList.length;
    show();
  }

  function close() {
    var v = lb.querySelector("video");
    if (v) v.pause();
    lb.classList.remove("open");
    document.body.style.overflow = "";
    cur = -1;
  }

  syncBar();
  render();
})();
