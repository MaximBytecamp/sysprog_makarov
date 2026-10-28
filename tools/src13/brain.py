"""Мозг агента: загружает ядро на C и получает сведения о системе."""
import ctypes
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
    ]


core = ctypes.CDLL(str(CORE_DIR / LIB_NAME))
core.core_get_info.argtypes = [ctypes.POINTER(CoreInfo)]
core.core_get_info.restype = ctypes.c_int


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
    }


def send(message, url):
    data = json.dumps(message, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.status, response.read().decode("utf-8")


if __name__ == "__main__":
    message = {"event": "agent_started", "os": sys.platform, **get_info()}
    print(json.dumps(message, ensure_ascii=False, indent=2))
    if len(sys.argv) > 1:
        status, body = send(message, sys.argv[1])
        print("n8n:", status, body)
