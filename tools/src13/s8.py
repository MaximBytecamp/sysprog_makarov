page.locator('[data-test-id="parameter-input-httpMethod"]').click(); time.sleep(1)
page.get_by_role('option', name='POST', exact=True).click(); time.sleep(1)
f = page.locator('[data-test-id="parameter-input-path"] input').first
f.click(); page.keyboard.press('Meta+A'); page.keyboard.type('agent'); time.sleep(0.5)
page.locator('text=HTTP Method').first.click(); time.sleep(1.5)
url = page.locator('text=/localhost:5678\\/webhook-test\\/agent/').first
print(url.count(), url.inner_text() if url.count() else '')
shot('04-webhook', [url, page.locator('[data-test-id="parameter-input-httpMethod"]'), page.locator('[data-test-id="parameter-input-path"]')])
