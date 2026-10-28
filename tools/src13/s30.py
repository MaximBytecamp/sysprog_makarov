p2 = ctx.new_page()
c2 = ctx.new_cdp_session(p2); c2.send('Emulation.setDeviceMetricsOverride', {'width': 1280, 'height': 800, 'deviceScaleFactor': 2, 'mobile': False})
p2.goto('http://localhost:8025/'); time.sleep(3)
p2.get_by_text('Агент-сторож: agent_started').first.click(); time.sleep(3)
p2.screenshot(path='/private/tmp/n30.png')
import json
open('/private/tmp/n30.json','w').write(json.dumps(p2.evaluate("""(()=>{const r=[];for(const s of ['Агент-сторож: agent_started','Это событие','"event"']){const e=[...document.querySelectorAll('*')].find(x=>x.childElementCount==0 && x.textContent.includes(s)); if(e){const b=e.getBoundingClientRect(); r.push([s,b.x,b.y,b.width,b.height])}} return r})()"""), ensure_ascii=False))
print(open('/private/tmp/n30.json').read())
