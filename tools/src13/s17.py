items = page.locator('[data-test-id="node-creator-node-item"]')
shot('08-ollama-pick', [page.locator('[data-test-id="node-creator-search-bar"]').first, items.nth(1)])
items.nth(1).click(); time.sleep(3)
page.screenshot(path='/private/tmp/n17.png')
