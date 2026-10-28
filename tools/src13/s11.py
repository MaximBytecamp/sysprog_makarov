page.keyboard.press('Escape'); time.sleep(1.5)
print(page.evaluate("""[...document.querySelectorAll('[data-test-id]')].map(e=>e.dataset.testId).filter(x=>/plus|handle|add|endpoint/i.test(x)).slice(0,20)"""))
page.screenshot(path='/private/tmp/n11.png')
