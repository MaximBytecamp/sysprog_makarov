import ctypes
import os
import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent.parent / "core"
LIB_NAME = {"win32": "sentry_core.dll", "darwin": "libsentry_core.dylib"}.get(sys.platform, "libsentry_core.so")


class CoreInfo(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_int64),
        ("page_size", ctypes.c_int32),
        ("cpus", ctypes.c_int32),
        ("host", ctypes.c_char * 256),
    ]


core = ctypes.CDLL(str(CORE_DIR / LIB_NAME))
core.core_get_info.argtypes = [ctypes.POINTER(CoreInfo)]
core.core_get_info.restype = ctypes.c_int

info = CoreInfo()
err = core.core_get_info(ctypes.byref(info))
print("err      ", err)
print("pid      ", info.pid, "  os.getpid():", os.getpid())
print("cpus     ", info.cpus)
print("page_size", info.page_size)
print("host     ", info.host)
