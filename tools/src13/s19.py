page.screenshot(path='/private/tmp/n19a.png')
url = page.locator('input[value="http://localhost:11434"]').first
save = page.get_by_role('button', name='Save').first
shot('09-credential', [url, save])
save.click(); time.sleep(4)
page.screenshot(path='/private/tmp/n19b.png')
