import ctypes
import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent.parent / "core"
LIB_NAME = {"win32": "sentry_core.dll", "darwin": "libsentry_core.dylib"}.get(sys.platform, "libsentry_core.so")

core = ctypes.CDLL(str(CORE_DIR / LIB_NAME))
print(core)
print(core.core_get_info)
