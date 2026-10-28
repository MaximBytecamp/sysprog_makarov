page.mouse.click(1235, 45); time.sleep(2)
page.keyboard.press('Shift+1'); time.sleep(0.5)
page.locator('[data-test-id="zoom-to-fit"]').first.click() if page.locator('[data-test-id="zoom-to-fit"]').count() else None
time.sleep(2)
page.screenshot(path='/private/tmp/n32.png')
print(page.evaluate("""[...document.querySelectorAll('[data-test-id]')].map(e=>e.dataset.testId).filter(x=>/publish|zoom|save/i.test(x))"""))
