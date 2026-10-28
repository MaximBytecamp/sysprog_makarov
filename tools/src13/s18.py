page.get_by_text('Connect to Ollama').click(); time.sleep(3)
page.screenshot(path='/private/tmp/n18.png')
print(page.evaluate("""[...document.querySelectorAll('input')].filter(i=>i.offsetParent).map(i=>[i.value,i.placeholder,i.name])"""))
