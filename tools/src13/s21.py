page.locator('#app-modals').get_by_role('button', name='Execute step').first.click()
for i in range(60):
    time.sleep(3)
    t = page.locator('#app-modals').inner_text()
    if 'No output data' not in t and ('text' in t) and 'Executing' not in t:
        break
time.sleep(4)
page.screenshot(path='/private/tmp/n21.png')
