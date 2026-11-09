"""Мозг агента: загружает ядро на C и получает сведения о системе."""
import ctypes
import errno
import json
import os
import sys
import urllib.request
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent.parent / "core"
LIB_NAME = {"win32": "sentry_core.dll", "darwin": "libsentry_core.dylib"}.get(sys.platform, "libsentry_core.so")


class CoreInfo(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_int64),
        ("cpus", ctypes.c_int32),
        ("page_size", ctypes.c_int32),
        ("host", ctypes.c_char * 256),
        ("uptime_s", ctypes.c_int64),
    ]


class CoreProc(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_int64),
        ("ppid", ctypes.c_int64),
        ("name", ctypes.c_char * 64),
    ]


class CoreChild(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_int64),
        ("handle", ctypes.c_int64),
    ]


core = ctypes.CDLL(str(CORE_DIR / LIB_NAME))
core.core_get_info.argtypes = [ctypes.POINTER(CoreInfo)]
core.core_get_info.restype = ctypes.c_int
core.core_list_procs.argtypes = [ctypes.POINTER(CoreProc), ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
core.core_list_procs.restype = ctypes.c_int
core.core_spawn.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(CoreChild)]
core.core_spawn.restype = ctypes.c_int
core.core_wait.argtypes = [ctypes.POINTER(CoreChild), ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
core.core_wait.restype = ctypes.c_int
TOO_SMALL = 122 if sys.platform == "win32" else errno.ERANGE


def error_text(code):
    if sys.platform == "win32":
        return ctypes.FormatError(code)
    return os.strerror(code)


def get_info():
    info = CoreInfo()
    err = core.core_get_info(ctypes.byref(info))
    if err != 0:
        raise OSError(err, error_text(err))
    return {
        "pid": info.pid,
        "cpus": info.cpus,
        "page_size": info.page_size,
        "host": info.host.decode("utf-8"),
        "uptime_s": info.uptime_s,
    }


def list_procs(room=256):
    while True:
        buf = (CoreProc * room)()
        count = ctypes.c_int32()
        err = core.core_list_procs(buf, room, ctypes.byref(count))
        if err == 0:
            return [{"pid": p.pid, "ppid": p.ppid, "name": p.name.decode("utf-8", "replace")}
                    for p in buf[:count.value]]
        if err != TOO_SMALL:
            raise OSError(err, error_text(err))
        room = count.value + 64


def parents(procs, pid):
    by_pid = {p["pid"]: p for p in procs}
    chain = []
    while pid in by_pid and len(chain) < 64:
        p = by_pid[pid]
        chain.append(p)
        if p["ppid"] == pid:
            break
        pid = p["ppid"]
    return chain


def spawn(args):
    argv = (ctypes.c_char_p * (len(args) + 1))(*[a.encode("utf-8") for a in args], None)
    child = CoreChild()
    err = core.core_spawn(argv, ctypes.byref(child))
    if err != 0:
        raise OSError(err, error_text(err))
    return child


def wait(child, timeout_ms=-1):
    code = ctypes.c_int32()
    err = core.core_wait(ctypes.byref(child), timeout_ms, ctypes.byref(code))
    if err != 0:
        raise OSError(err, error_text(err))
    return code.value


def send(message, url):
    data = json.dumps(message, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.status, response.read().decode("utf-8")


if __name__ == "__main__":
    child = spawn([sys.executable, "-c", "import time; time.sleep(1); raise SystemExit(3)"])
    procs = list_procs()
    chain = parents(procs, child.pid)
    code = wait(child, 5000)
    message = {"event": "agent_started", "os": sys.platform, **get_info(),
               "procs": len(procs), "child": child.pid, "child_code": code,
               "parents": [p["name"] for p in chain]}
    print(json.dumps(message, ensure_ascii=False, indent=2))
    if len(sys.argv) > 1:
        status, body = send(message, sys.argv[1])
        print("n8n:", status, body)
