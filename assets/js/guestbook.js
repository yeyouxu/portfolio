/* 留言板（共享版，支持 公开 / 不公开）
   公开留言：所有访客可见；不公开留言：只有网站主人在后台可见。

   —— 启用方法（一次性，约 5 分钟，免费）——
   1. 打开 https://supabase.com ，用 GitHub 账号登录 → New project
      （名字随意，地区选 Singapore，数据库密码点 Generate 存好）
   2. 左侧 SQL Editor → New query → 粘贴下面这段 → Run：

      create table messages (
        id bigint generated always as identity primary key,
        name text default '路过的风',
        msg text not null,
        is_public boolean default true,
        created_at timestamptz default now()
      );
      alter table messages enable row level security;
      create policy "anyone can post" on messages for insert with check (true);
      create policy "public read" on messages for select using (is_public = true);

   3. 左侧 Project Settings → API → 复制 Project URL 和 anon public key
   4. 把两个值填到下面 GB_CONFIG 的两行引号里，保存提交即可。
   5. 查看不公开留言：supabase.com 左侧 Table Editor → messages 表，
      is_public = false 的行就是只有你能看见的留言。

   未配置 GB_CONFIG 时：留言只保存在访客自己的浏览器里（旧行为）。
*/
(function () {
  "use strict";

  var GB_CONFIG = {
    url: "",       // ← 填 Project URL，如 https://abcdefgh.supabase.co
    anonKey: ""    // ← 填 anon public key
  };

  var KEY = "yeji_guestbook_v1";
  var form = document.getElementById("gbForm");
  var list = document.getElementById("gbList");
  if (!form || !list) return;

  var remote = !!(GB_CONFIG.url && GB_CONFIG.anonKey);

  function esc(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function fmt(ts) {
    var d = new Date(ts);
    var p = function (n) { return (n < 10 ? "0" : "") + n; };
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) +
           " " + p(d.getHours()) + ":" + p(d.getMinutes());
  }

  /* 管理模式：网址后加 ?admin=1 时，每条留言旁显示删除按钮（仅网站主人使用） */
  var ADMIN = new URLSearchParams(location.search).has("admin");

  function renderItems(items) {
    list.innerHTML = "";
    if (!items.length) {
      var empty = document.createElement("p");
      empty.className = "gb-empty";
      empty.textContent = "这里还很安静，写下第一句话吧。";
      list.appendChild(empty);
      return;
    }
    items.forEach(function (it) {
      var div = document.createElement("div");
      div.className = "gb-item" + (ADMIN ? " admin" : "");
      div.innerHTML =
        '<div class="gb-head"><span class="gb-name">' + esc(it.name) + "</span>" +
        '<span class="gb-date">' + fmt(it.ts) + "</span></div>" +
        '<p class="gb-msg">' + esc(it.msg) + "</p>";
      if (ADMIN) {
        var del = document.createElement("button");
        del.className = "gb-del";
        del.title = "删除这条留言";
        del.innerHTML = "×";
        del.addEventListener("click", function () { removeItem(it); });
        div.appendChild(del);
      }
      list.appendChild(div);
    });
  }

  /* 删除一条留言：本地模式删 localStorage；共享模式调 Supabase DELETE */
  function removeItem(it) {
    if (!confirm("删掉这条留言吗？（不可恢复）")) return;
    if (remote) {
      fetch(GB_CONFIG.url + "/rest/v1/messages?id=eq." + it.id, {
        method: "DELETE",
        headers: { apikey: GB_CONFIG.anonKey, Authorization: "Bearer " + GB_CONFIG.anonKey }
      }).then(function (r) {
        if (r.ok) { loadRemote(); }
        else { alert("没删掉——需要在 Supabase 给 messages 表加一条 delete policy（允许 anon 删除）。"); }
      }).catch(function () { alert("网络不好，没删掉，稍后再试。"); });
    } else {
      var items = loadLocal().filter(function (x) { return x.ts !== it.ts; });
      saveLocal(items);
      renderItems(items);
    }
  }

  /* ---------- 本地模式（未配置后端时） ---------- */
  function loadLocal() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; }
    catch (e) { return []; }
  }
  function saveLocal(items) {
    try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) {}
  }

  /* ---------- 共享模式（Supabase） ---------- */
  function loadRemote() {
    list.innerHTML = '<p class="gb-empty">正在翻开留言……</p>';
    fetch(GB_CONFIG.url + "/rest/v1/messages?is_public=eq.true&order=created_at.desc&limit=50", {
      headers: { apikey: GB_CONFIG.anonKey, Authorization: "Bearer " + GB_CONFIG.anonKey }
    })
      .then(function (r) { return r.json(); })
      .then(function (rows) {
        renderItems(rows.map(function (r) {
          return { id: r.id, name: r.name, msg: r.msg, ts: r.created_at };
        }));
      })
      .catch(function () {
        list.innerHTML = '<p class="gb-empty">留言板暂时打不开，稍后再来看看。</p>';
      });
  }

  function postRemote(name, msg, isPublic, done, fail) {
    fetch(GB_CONFIG.url + "/rest/v1/messages", {
      method: "POST",
      headers: {
        apikey: GB_CONFIG.anonKey,
        Authorization: "Bearer " + GB_CONFIG.anonKey,
        "Content-Type": "application/json",
        Prefer: "return=minimal"
      },
      body: JSON.stringify({ name: name, msg: msg, is_public: isPublic })
    }).then(function (r) {
      if (r.ok) { done(); } else { fail(); }
    }).catch(fail);
  }

  /* ---------- 提交 ---------- */
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var nameEl = form.querySelector("input[name=name]");
    var msgEl = form.querySelector("textarea[name=msg]");
    var visEl = form.querySelector("input[name=vis]:checked");
    var name = nameEl.value.trim().slice(0, 20) || "路过的风";
    var msg = msgEl.value.trim().slice(0, 300);
    var isPublic = !visEl || visEl.value === "public";
    if (!msg) { msgEl.focus(); return; }

    var btn = form.querySelector(".gb-submit");
    var old = btn.textContent;
    btn.disabled = true;

    function ok() {
      msgEl.value = "";
      btn.textContent = isPublic ? "已留下足迹" : "已悄悄寄给主人";
      if (remote) { loadRemote(); } else {
        var items = loadLocal();
        items.unshift({ name: name, msg: msg, ts: Date.now() });
        saveLocal(items.slice(0, 100));
        renderItems(loadLocal());
      }
      setTimeout(function () { btn.textContent = old; btn.disabled = false; }, 1800);
    }
    function fail() {
      btn.textContent = "没寄出去，再试一次";
      setTimeout(function () { btn.textContent = old; btn.disabled = false; }, 1800);
    }

    if (remote) { postRemote(name, msg, isPublic, ok, fail); }
    else { ok(); }
  });

  /* ---------- 初始化 ---------- */
  if (remote) { loadRemote(); } else { renderItems(loadLocal()); }
})();
