model = page.locator('[data-test-id="parameter-input-model"]').first
model.click(); time.sleep(2.5)
opt = page.get_by_role('option', name='qwen2.5:3b').first
print(page.get_by_role('option').count(), opt.count())
time.sleep(5)  # уходит уведомление
shot('10-model', [model, opt])
opt.click(); time.sleep(1.5)
page.screenshot(path='/private/tmp/n20.png')
