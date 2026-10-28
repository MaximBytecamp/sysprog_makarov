page.get_by_role('option').first.click(); time.sleep(1.5)
el = page.locator('[data-test-id="parameter-input-text"] textarea, [data-test-id="parameter-input-text"] input').first
el.fill("{{ $json.text }}\n\nСообщение агента:\n{{ JSON.stringify($('Webhook').item.json.body, null, 2) }}"); time.sleep(1)
page.locator('text=Operation').first.click(); time.sleep(1.5)
page.screenshot(path='/private/tmp/n28.png')
