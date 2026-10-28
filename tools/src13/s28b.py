o = page.get_by_role('option'); print([o.nth(i).inner_text()[:30] for i in range(o.count())])
page.screenshot(path='/private/tmp/n28.png')
