/* 首屏星空：星星闪烁 + 鼠标悬停点亮周围的星星（连成星座） */
(function () {
  "use strict";

  var canvas = document.getElementById("starCanvas");
  if (!canvas) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var ctx = canvas.getContext("2d");
  var stars = [];
  var mouse = { x: -9999, y: -9999 };
  var W = 0, H = 0, DPR = 1;
  var LIGHT_RADIUS = 160;   // 点亮半径
  var LINK_DIST = 90;       // 被点亮的星星之间连线距离

  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth;
    H = canvas.clientHeight;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    seed();
  }

  function seed() {
    stars = [];
    var count = Math.floor((W * H) / 2600); // 密度随面积
    for (var i = 0; i < count; i++) {
      var gold = Math.random() < 0.14;
      stars.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.3 + 0.4,
        baseA: Math.random() * 0.45 + 0.2,
        twSpeed: Math.random() * 0.9 + 0.35,
        phase: Math.random() * Math.PI * 2,
        gold: gold,
        lit: 0 // 0~1 被点亮程度
      });
    }
  }

  var last = performance.now();
  function frame(now) {
    var dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    var t = now / 1000;
    ctx.clearRect(0, 0, W, H);

    var i, s;
    // 更新点亮程度（柔和趋近）
    for (i = 0; i < stars.length; i++) {
      s = stars[i];
      var dx = s.x - mouse.x, dy = s.y - mouse.y;
      var d = Math.sqrt(dx * dx + dy * dy);
      var target = d < LIGHT_RADIUS ? 1 - d / LIGHT_RADIUS : 0;
      s.lit += (target - s.lit) * Math.min(dt * 6, 1);
    }

    // 被点亮星星之间的细连线（星座感）
    ctx.lineWidth = 0.5;
    for (i = 0; i < stars.length; i++) {
      var a = stars[i];
      if (a.lit < 0.25) continue;
      for (var j = i + 1; j < stars.length; j++) {
        var b = stars[j];
        if (b.lit < 0.25) continue;
        var ddx = a.x - b.x, ddy = a.y - b.y;
        var dd = Math.sqrt(ddx * ddx + ddy * ddy);
        if (dd < LINK_DIST) {
          var la = Math.min(a.lit, b.lit) * (1 - dd / LINK_DIST) * 0.5;
          ctx.strokeStyle = "rgba(217, 192, 138," + la.toFixed(3) + ")";
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    // 画星星
    for (i = 0; i < stars.length; i++) {
      s = stars[i];
      var tw = 0.5 + 0.5 * Math.sin(t * s.twSpeed + s.phase); // 闪烁
      var alpha = s.baseA * (0.45 + 0.55 * tw) + s.lit * 0.75;
      var radius = s.r * (1 + s.lit * 1.6);
      if (alpha > 1) alpha = 1;

      // 光晕
      if (s.lit > 0.03) {
        var g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, radius * 7);
        g.addColorStop(0, "rgba(217,192,138," + (s.lit * 0.32).toFixed(3) + ")");
        g.addColorStop(1, "rgba(217,192,138,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(s.x, s.y, radius * 7, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.fillStyle = s.gold
        ? "rgba(217,192,138," + alpha.toFixed(3) + ")"
        : "rgba(236,233,222," + alpha.toFixed(3) + ")";
      ctx.beginPath();
      ctx.arc(s.x, s.y, radius, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(frame);
  }

  var hero = canvas.parentElement;
  hero.addEventListener("mousemove", function (e) {
    var rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });
  hero.addEventListener("mouseleave", function () {
    mouse.x = -9999;
    mouse.y = -9999;
  });
  // 触屏：手指划过也点亮
  hero.addEventListener("touchmove", function (e) {
    var rect = canvas.getBoundingClientRect();
    var tc = e.touches[0];
    mouse.x = tc.clientX - rect.left;
    mouse.y = tc.clientY - rect.top;
  }, { passive: true });
  hero.addEventListener("touchend", function () {
    mouse.x = -9999;
    mouse.y = -9999;
  });

  window.addEventListener("resize", resize);
  resize();
  requestAnimationFrame(frame);
})();
