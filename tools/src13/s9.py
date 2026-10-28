import subprocess
page.get_by_role('button', name='Listen for test event').first.click(); time.sleep(2)
r = subprocess.run(['/Users/makarovmn/.pyenv/versions/3.12.12/bin/python3', 'brain.py', 'http://localhost:5678/webhook-test/agent'], cwd='/private/tmp/sp13/sysprog-start/agent/brain', capture_output=True, text=True)
print(r.stdout, r.stderr[-300:])
open('/Users/makarovmn/sysprog-shots/m13/out-test.txt','w').write(r.stdout)
time.sleep(2)
page.get_by_text('JSON', exact=True).first.click(); time.sleep(1)
page.mouse.move(640, 700); time.sleep(6)
body = page.locator('text="body"').first
print(body.count())
page.screenshot(path='/private/tmp/n9c.png')
