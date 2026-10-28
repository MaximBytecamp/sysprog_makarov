page.get_by_text('Sends an email using SMTP protocol').click(); time.sleep(2)
page.screenshot(path='/private/tmp/n24.png')
print(page.evaluate("""[...document.querySelectorAll('[data-test-id]')].filter(e=>/action/i.test(e.dataset.testId)).map(e=>e.dataset.testId+': '+e.innerText.slice(0,40))"""))
