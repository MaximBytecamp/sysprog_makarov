import subprocess
inp = page.locator('#app-modals input').first
inp.fill('v1: письмо с объяснением модели'); time.sleep(0.8)
btn = page.locator('#app-modals').get_by_role('button', name='Publish').first
shot('17-publish', [inp, btn])
btn.click(); time.sleep(4)
page.screenshot(path='/private/tmp/n34a.png')
r = subprocess.run(['/Users/makarovmn/.pyenv/versions/3.12.12/bin/python3', 'brain.py', 'http://localhost:5678/webhook/agent'], cwd='/private/tmp/sp13/sysprog-start/agent/brain', capture_output=True, text=True)
print(r.stdout, r.stderr[-300:]); open('/Users/makarovmn/sysprog-shots/m13/out-prod.txt','w').write(r.stdout)
time.sleep(60)
page.get_by_text('Executions', exact=True).first.click(); time.sleep(4)
page.screenshot(path='/private/tmp/n34b.png')
