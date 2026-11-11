import ctypes, sys, threading, time
lib = ctypes.CDLL("./libburn.dylib")
lib.burn.argtypes = [ctypes.c_int64]; lib.burn.restype = ctypes.c_int64
N = 2_000_000_000
for k in (1, 4):
    ts = [threading.Thread(target=lib.burn, args=(N // k,)) for _ in range(k)]
    s = time.perf_counter(); [t.start() for t in ts]; [t.join() for t in ts]
    print(sys._is_gil_enabled(), k, f"{time.perf_counter() - s:.2f}")
