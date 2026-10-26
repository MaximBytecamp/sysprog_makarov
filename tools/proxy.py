"""Небольшой HTTP-прокси (CONNECT и обычные запросы) для ВМ: имена разрешает хост."""
import asyncio

async def pipe(r, w):
    try:
        while data := await r.read(65536):
            w.write(data); await w.drain()
    except Exception:
        pass
    finally:
        try: w.close()
        except Exception: pass

async def handle(cr, cw):
    try:
        head = await cr.readuntil(b'\r\n\r\n')
    except Exception:
        cw.close(); return
    line = head.split(b'\r\n')[0].decode(errors='replace')
    method, target, _ = line.split(' ', 2)
    if method == 'CONNECT':
        host, port = target.rsplit(':', 1)
        try:
            ur, uw = await asyncio.open_connection(host, int(port))
        except Exception:
            cw.write(b'HTTP/1.1 502 Bad Gateway\r\n\r\n'); await cw.drain(); cw.close(); return
        cw.write(b'HTTP/1.1 200 Connection Established\r\n\r\n'); await cw.drain()
        await asyncio.gather(pipe(cr, uw), pipe(ur, cw))
    else:
        from urllib.parse import urlsplit
        u = urlsplit(target); host = u.hostname; port = u.port or 80
        path = (u.path or '/') + ('?' + u.query if u.query else '')
        try:
            ur, uw = await asyncio.open_connection(host, port)
        except Exception:
            cw.write(b'HTTP/1.1 502 Bad Gateway\r\n\r\n'); await cw.drain(); cw.close(); return
        rest = head.split(b'\r\n', 1)[1]
        uw.write(f'{method} {path} HTTP/1.1\r\n'.encode() + rest); await uw.drain()
        await asyncio.gather(pipe(cr, uw), pipe(ur, cw))

async def main():
    srv = await asyncio.start_server(handle, '0.0.0.0', 8899)
    async with srv: await srv.serve_forever()

asyncio.run(main())
