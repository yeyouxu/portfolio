/* 通用交互：导航、入场淡入、视差滚动、灯箱 */
(function () {
  "use strict";

  /* ---------- 导航：滚动加深 & 移动端展开 ---------- */
  var nav = document.querySelector(".nav");
  function onNavScroll() {
    if (window.scrollY > 30) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  }
  if (nav) {
    window.addEventListener("scroll", onNavScroll, { passive: true });
    onNavScroll();
  }

  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      toggle.classList.toggle("open");
      links.classList.toggle("open");
      document.body.style.overflow = links.classList.contains("open") ? "hidden" : "";
    });
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        toggle.classList.remove("open");
        links.classList.remove("open");
        document.body.style.overflow = "";
      }
    });
  }

  /* ---------- 入场：从下往上淡入 ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("visible");
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("visible"); });
  }

  /* ---------- 视差滚动 ---------- */
  var pxEls = Array.prototype.slice.call(document.querySelectorAll("[data-parallax]"));
  if (pxEls.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var vh = window.innerHeight;
        pxEls.forEach(function (el) {
          var rect = el.parentElement.getBoundingClientRect();
          if (rect.bottom < 0 || rect.top > vh) return;
          var speed = parseFloat(el.getAttribute("data-parallax")) || 0.25;
          var progress = (rect.top + rect.height / 2 - vh / 2) / vh; // -0.5 ~ 0.5 附近
          el.style.transform = "translateY(" + (progress * speed * -100).toFixed(2) + "%)";
        });
        ticking = false;
      });
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();
  }

  /* ---------- 灯箱 ---------- */
  var lb = document.createElement("div");
  lb.className = "lightbox";
  lb.innerHTML =
    '<button class="lightbox-close" aria-label="关闭">×</button>' +
    '<div class="lightbox-box"><div class="lightbox-media"></div>' +
    '<p class="lightbox-caption"></p></div>';
  document.body.appendChild(lb);

  var lbMedia = lb.querySelector(".lightbox-media");
  var lbCaption = lb.querySelector(".lightbox-caption");

  function closeLb() {
    lb.classList.remove("open");
    document.body.style.overflow = "";
    setTimeout(function () { lbMedia.innerHTML = ""; }, 500);
  }

  window.openLightbox = function (work) {
    lbMedia.innerHTML = "";
    if (work.type === "video" && work.video) {
      var v = document.createElement("video");
      v.src = work.video;
      v.controls = true;
      v.autoplay = true;
      v.loop = true;
      v.muted = true;
      v.playsInline = true;
      lbMedia.appendChild(v);
    } else {
      var img = document.createElement("img");
      img.src = work.src;
      img.alt = work.title;
      lbMedia.appendChild(img);
    }
    lbCaption.textContent = work.title + " · " + work.desc;
    lb.classList.add("open");
    document.body.style.overflow = "hidden";
  };

  lb.addEventListener("click", function (e) {
    if (e.target === lb || e.target.closest(".lightbox-close")) closeLb();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && lb.classList.contains("open")) closeLb();
  });

  /* ---------- 页脚年份 ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- 防下载（常规防护：禁右键 / 禁拖拽；输入框除外） ---------- */
  document.addEventListener("contextmenu", function (e) {
    if (e.target.closest("input, textarea, .gb-form")) return;
    e.preventDefault();
  });
  document.addEventListener("dragstart", function (e) {
    if (e.target.tagName === "IMG" || e.target.tagName === "VIDEO") e.preventDefault();
  });

  /* ---------- 回到顶部（长页面滚动后出现） ---------- */
  var topBtn = document.createElement("button");
  topBtn.className = "to-top";
  topBtn.setAttribute("aria-label", "回到顶部");
  topBtn.innerHTML = "↑";
  document.body.appendChild(topBtn);
  topBtn.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  function onScrollTop() {
    topBtn.classList.toggle("show", window.scrollY > 600);
  }
  window.addEventListener("scroll", onScrollTop, { passive: true });
  onScrollTop();
})();
