import json
p2 = [p for p in ctx.pages if '8025' in p.url][0]
c2 = ctx.new_cdp_session(p2); c2.send('Emulation.setDeviceMetricsOverride', {'width': 1280, 'height': 800, 'deviceScaleFactor': 2, 'mobile': False})
time.sleep(1); p2.screenshot(path='/Users/makarovmn/sysprog-shots/m13/raw/15-mail.png')
db = json.loads(open('/Users/makarovmn/sysprog-shots/m13/marks.json').read())
db['15-mail'] = [[449, 120, 463, 26], [328, 262, 928, 40], [328, 330, 290, 176]]
open('/Users/makarovmn/sysprog-shots/m13/marks.json','w').write(json.dumps(db, ensure_ascii=False, indent=1))
p2.close()
