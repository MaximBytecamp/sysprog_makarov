act = page.get_by_text('Send an Email', exact=True).first
shot('12-email-pick', [act])
act.click(); time.sleep(3)
page.screenshot(path='/private/tmp/n25.png')
print(page.evaluate("""[...document.querySelectorAll('[data-test-id^="parameter-input-"]')].map(e=>e.dataset.testId).filter(x=>!/field|hint|item/.test(x))"""))
