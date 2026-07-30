# -*- coding: utf-8 -*-
"""临时本地 CONNECT 代理：把 github.com 的 443 转发到可用 IP，绕过 DNS 污染。
仅监听 127.0.0.1，仅供本机 git 使用。"""
import select
import socket
import threading

UPSTREAM = "140.82.113.3"   # 已验证可连的 github.com IP
LISTEN_PORT = 8443


def pipe(a, b):
    try:
        while True:
            r, _, _ = select.select([a, b], [], [], 120)
            if not r:
                break
            for s in r:
                try:
                    data = s.recv(65536)
                except OSError:
                    return
                if not data:
                    return
                (b if s is a else a).sendall(data)
    except OSError:
        pass


def handle(conn):
    try:
        req = b""
        while b"\r\n\r\n" not in req:
            chunk = conn.recv(4096)
            if not chunk:
                return
            req += chunk
        line = req.split(b"\r\n", 1)[0].decode("latin1")
        parts = line.split(" ")
        target = parts[1]
        host = target.split(":")[0]
        port = int(target.split(":")[1]) if ":" in target else 443
        dest_ip = UPSTREAM if host == "github.com" else socket.gethostbyname(host)
        up = socket.create_connection((dest_ip, port), timeout=15)
        conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        pipe(conn, up)
        try:
            up.close()
        except Exception:
            pass
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", LISTEN_PORT))
    srv.listen(50)
    print("proxy ready on 127.0.0.1:%d -> github.com=%s" % (LISTEN_PORT, UPSTREAM), flush=True)
    while True:
        c, _ = srv.accept()
        threading.Thread(target=handle, args=(c,), daemon=True).start()


if __name__ == "__main__":
    main()
