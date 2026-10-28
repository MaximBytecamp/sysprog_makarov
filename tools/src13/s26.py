page.get_by_text('Connect to SMTP').click(); time.sleep(3)
page.screenshot(path='/private/tmp/n26.png')
print(page.evaluate("""[...document.querySelectorAll('[data-test-id^="parameter-input-"]')].filter(e=>e.offsetParent).map(e=>e.dataset.testId).filter(x=>!/field|hint|item/.test(x))"""))
