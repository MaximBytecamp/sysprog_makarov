page.goto('http://localhost:5678/home/workflows'); time.sleep(3)
b = page.get_by_text('Build a workflow')
card = b.locator('xpath=ancestor::*[self::button or self::a or contains(@class,"card") or contains(@class,"Card")][1]')
target = card if card.count() else b
shot('02-home', [target])
target.click(); time.sleep(4)
page.screenshot(path='/private/tmp/n3.png'); print(page.url)
