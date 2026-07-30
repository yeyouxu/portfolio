# -*- coding: utf-8 -*-
"""逐文件推送器：把本地 ed94363 相对远程 49f1b2b 的变更，经 GitHub Contents API
逐个文件上传并移动 main 引用。替代 git push 单连接大传输（会被网络重置）。
用法：python api_push.py <token>   （token 从 wincred 读取后由调用方传入）
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

REPO = "yeyouxu/portfolio"
BASE = "https://api.github.com"
ROOT = r"E:\3 workbuddy\portfolio"
PROXY = "http://127.0.0.1:8443"   # 本地中转（github.com 走可用 IP）


def _read_cred(target):
    """用 Win32 CredReadW 读通用凭据的密码。"""
    import ctypes
    from ctypes import wintypes

    class CREDENTIALW(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
            ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD),
            ("Attributes", wintypes.LPVOID), ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR)]

    adv = ctypes.windll.advapi32
    pcred = ctypes.POINTER(CREDENTIALW)()
    if not adv.CredReadW(target, 1, 0, ctypes.byref(pcred)):
        return None
    try:
        size = pcred.contents.CredentialBlobSize
        blob = ctypes.string_at(pcred.contents.CredentialBlob, size)
        return blob.decode("utf-16-le", "ignore").rstrip("\x00")
    finally:
        adv.CredFree(pcred)


def get_token():
    """优先用 git:https://dayang919@github.com 条目里的 OAuth token（改名后仍有效）。"""
    for target in ("git:https://dayang919@github.com",
                   "GitHub - https://api.github.com/yeyouxu"):
        t = _read_cred(target)
        if t:
            return t
    p = subprocess.run(["git", "credential", "fill"],
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True, cwd=ROOT)
    for line in p.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password="):].strip()
    raise RuntimeError("没有可用的 github.com 凭据")


TOKEN = get_token()
LOCAL_HEAD = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
REMOTE_MAIN = "4610d1a9d2dc78aa6222310d013f5d9f5d059388"  # 新仓库起点


def api(method, path, payload=None, use_proxy=False, retries=5):
    url = BASE + path
    handlers = []
    if use_proxy:
        handlers.append(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    else:
        handlers.append(urllib.request.ProxyHandler({}))
    opener = urllib.request.build_opener(*handlers)
    for attempt in range(retries):
        try:
            data = json.dumps(payload).encode() if payload is not None else None
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("Authorization", "token " + TOKEN)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("User-Agent", "yeji-uploader")
            if payload is not None:
                req.add_header("Content-Type", "application/json")
            with opener.open(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            print("  HTTP %s %s (%s)" % (e.code, path, body), flush=True)
            if e.code in (403, 404, 422):
                raise
        except Exception as e:
            print("  网络错误 %s，重试 %d/%d" % (e, attempt + 1, retries), flush=True)
            time.sleep(4)
    raise RuntimeError("API 失败: " + path)


def get_changes():
    out = subprocess.check_output(
        ["git", "-c", "core.quotepath=false", "diff", "--name-status", REMOTE_MAIN, LOCAL_HEAD],
        cwd=ROOT).decode("utf-8", "replace")
    modified, deleted = [], []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        if status.startswith("D"):
            deleted.append(path)
        else:
            modified.append(path)
    return modified, deleted


def blob_sha(path):
    with open(os.path.join(ROOT, path.replace("/", os.sep)), "rb") as f:
        content = f.read()
    payload = {"content": base64.b64encode(content).decode(), "encoding": "base64"}
    r = api("POST", "/repos/%s/git/blobs" % REPO, payload)
    return r["sha"]


def main():
    modified, deleted = get_changes()
    progress_path = os.path.join(ROOT, "tools", ".push_progress")
    done = set()
    if os.path.isfile(progress_path):
        with open(progress_path, encoding="utf-8") as f:
            done = set(x.strip() for x in f if x.strip())
    big = []
    todo = []
    for p in modified:
        if p == "tools/.push_progress":
            continue               # 进度记录文件本身不上传
        fp = os.path.join(ROOT, p.replace("/", os.sep))
        if os.path.getsize(fp) > 15 * 1024 * 1024:
            big.append(p)          # >15MB：API 单请求传不动，留给 git push 单独推
        elif p not in done:
            todo.append(p)
    print("待上传 %d 个（跳过已完成 %d），删除 %d 个，大文件暂缓 %d 个: %s"
          % (len(todo), len(done), len(deleted), len(big), big), flush=True)

    tree_items = []
    for p in todo:
        for attempt in range(5):
            try:
                sha = blob_sha(p)
                break
            except Exception as e:
                if attempt == 4:
                    raise
                print("  blob 重试 %s (%s)" % (p, e), flush=True)
                time.sleep(5)
        tree_items.append({"path": p, "mode": "100644", "type": "blob", "sha": sha})
        with open(progress_path, "a", encoding="utf-8") as f:
            f.write(p + "\n")
        if (len(tree_items)) % 20 == 0:
            print("  blob 进度 %d/%d" % (len(tree_items), len(todo)), flush=True)
    # 已传过的文件：二进制直接用本地 blob sha（字节一致）；
    # 文本文件可能因换行符/脚本自身变动导致 sha 不符，重新 POST（幂等，秒回）
    text_ext = (".html", ".css", ".js", ".py", ".md", ".txt", ".json", ".xml")
    for p in modified:
        if p in done:
            if p.lower().endswith(text_ext):
                sha = blob_sha(p)
            else:
                sha = subprocess.check_output(
                    ["git", "-c", "core.quotepath=false", "rev-parse", "HEAD:" + p],
                    cwd=ROOT).decode().strip()
            tree_items.append({"path": p, "mode": "100644", "type": "blob", "sha": sha})
    for p in deleted:
        tree_items.append({"path": p, "mode": "100644", "type": "blob", "sha": None})

    # 基 tree = 远程 commit 的 tree；分块增量建树（单次请求太大会 422）
    base_commit = api("GET", "/repos/%s/git/commits/%s" % (REPO, REMOTE_MAIN))
    tree_sha = base_commit["tree"]["sha"]
    CHUNK = 40
    for i in range(0, len(tree_items), CHUNK):
        chunk = tree_items[i:i + CHUNK]
        tree = api("POST", "/repos/%s/git/trees" % REPO,
                   {"base_tree": tree_sha, "tree": chunk})
        tree_sha = tree["sha"]
        print("tree 分块 %d/%d 完成" % (i // CHUNK + 1, (len(tree_items) + CHUNK - 1) // CHUNK), flush=True)

    commit = api("POST", "/repos/%s/git/commits" % REPO,
                 {"message": "上线：全部照片与页面（经 API 逐文件上传）",
                  "tree": tree_sha, "parents": [REMOTE_MAIN]})
    print("commit 创建完成: " + commit["sha"][:8], flush=True)

    api("PATCH", "/repos/%s/git/refs/heads/main" % REPO,
        {"sha": commit["sha"], "force": False})
    print("===== main 已更新到 %s =====" % commit["sha"][:8], flush=True)


if __name__ == "__main__":
    main()
