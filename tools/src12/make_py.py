"""Версии brain.py по шагам главы 1.2 → py/v*.py."""
from pathlib import Path
P = Path(__file__).parent / 'py'
HEAD = '''import ctypes
{os}import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent.parent / "core"
LIB_NAME = {{"win32": "sentry_core.dll", "darwin": "libsentry_core.dylib"}}.get(sys.platform, "libsentry_core.so")
'''
STRUCT = '''

class CoreInfo(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_int64),
        ("cpus", ctypes.c_int32),
        ("page_size", ctypes.c_int32),
        ("host", ctypes.c_char * 256),
    ]

'''
LOAD = '''
core = ctypes.CDLL(str(CORE_DIR / LIB_NAME))
'''
TYPES = '''core.core_get_info.argtypes = [ctypes.POINTER(CoreInfo)]
core.core_get_info.restype = ctypes.c_int
'''
CALL = '''
info = CoreInfo()
err = core.core_get_info(ctypes.byref(info))
print("err      ", err)
print("pid      ", info.pid, "  os.getpid():", os.getpid())
print("cpus     ", info.cpus)
print("page_size", info.page_size)
print("host     ", info.host)
'''
(P / 'v1_load.py').write_text(HEAD.format(os='') + LOAD + 'print(core)\nprint(core.core_get_info)\n')
(P / 'v2_struct.py').write_text(HEAD.format(os='') + STRUCT + '''
print("sizeof", ctypes.sizeof(CoreInfo))
for name, _ in CoreInfo._fields_:
    field = getattr(CoreInfo, name)
    print(f"{name:10} offset {field.offset:3}  size {field.size}")
''')
v3 = HEAD.format(os='import os\n') + STRUCT + LOAD + TYPES + CALL
(P / 'v3_call.py').write_text(v3)
sw = v3.replace('        ("cpus", ctypes.c_int32),\n        ("page_size", ctypes.c_int32),', '        ("page_size", ctypes.c_int32),\n        ("cpus", ctypes.c_int32),')
assert sw != v3
(P / 'v4_swap.py').write_text(sw)
(P / 'v5_null.py').write_text(HEAD.format(os='import os\n') + STRUCT + LOAD + TYPES + '''
err = core.core_get_info(None)
if sys.platform == "win32":
    print("err", err, ctypes.FormatError(err))
else:
    print("err", err, os.strerror(err))
''')
