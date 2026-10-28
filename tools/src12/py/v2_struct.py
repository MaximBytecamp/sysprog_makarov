import ctypes
import sys
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


print("sizeof", ctypes.sizeof(CoreInfo))
for name, _ in CoreInfo._fields_:
    field = getattr(CoreInfo, name)
    print(f"{name:10} offset {field.offset:3}  size {field.size}")
