host = page.locator('[data-test-id="parameter-input-host"] input').first
host.fill('localhost')
port = page.locator('[data-test-id="parameter-input-port"] input').first
port.fill('1025')
sec = page.locator('[data-test-id="parameter-input-secure"]').first
sec.locator('.el-switch, [role="switch"], input').first.click(); time.sleep(1)
page.mouse.move(640, 60); time.sleep(1)
shot('13-smtp', [page.locator('[data-test-id="parameter-input-host"]').first, page.locator('[data-test-id="parameter-input-port"]').first, sec, page.get_by_role('button', name='Save').first])
page.get_by_role('button', name='Save').first.click(); time.sleep(4)
page.screenshot(path='/private/tmp/n27.png')
