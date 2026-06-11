#!/usr/bin/env python3
import os
import socket
import threading

LISTEN_PATH = '/run/ops-tmux/default'
TARGET_PATH = '/tmp/tmux-0/default'

os.makedirs(os.path.dirname(LISTEN_PATH), exist_ok=True)
try:
    os.unlink(LISTEN_PATH)
except FileNotFoundError:
    pass

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(LISTEN_PATH)
os.chmod(LISTEN_PATH, 0o660)
server.listen(128)


def pump(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except Exception:
            pass


while True:
    client, _ = server.accept()
    try:
        upstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        upstream.connect(TARGET_PATH)
    except Exception:
        client.close()
        continue

    threading.Thread(target=pump, args=(client, upstream), daemon=True).start()
    threading.Thread(target=pump, args=(upstream, client), daemon=True).start()
