P = lambda n: page.locator(f'[data-test-id="parameter-input-{n}"]').first
shot('14-email', [P('toEmail'), P('subject'), P('text')])
page.locator('#app-modals').get_by_role('button', name='Execute step').first.click(); time.sleep(8)
page.screenshot(path='/private/tmp/n29.png')
