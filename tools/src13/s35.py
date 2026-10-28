shot('18-published', [[1122, 16, 106, 32], [433, 352, 420, 80]])
page.get_by_role('button', name='Got it').first.click(); time.sleep(2)
page.locator('[data-test-id="radio-button-executions"]').first.click(); time.sleep(4)
page.screenshot(path='/private/tmp/n35.png')
