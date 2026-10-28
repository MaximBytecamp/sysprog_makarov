def fill(name, value):
    el = page.locator(f'[data-test-id="parameter-input-{name}"] input, [data-test-id="parameter-input-{name}"] textarea').first
    el.fill(value); time.sleep(1)
    page.locator('text=Operation').first.click(); time.sleep(1)
fill('fromEmail', 'agent@sysprog.local')
fill('toEmail', 'ivan.petrov@example.com')
fill('subject', "Агент-сторож: {{ $('Webhook').item.json.body.event }} на {{ $('Webhook').item.json.body.host }}")
page.locator('[data-test-id="parameter-input-emailFormat"]').click(); time.sleep(1)
page.get_by_role('option', name='Text', exact=True).first.click(); time.sleep(1.5)
fill('text', "{{ $json.text }}\n\nСообщение агента:\n{{ JSON.stringify($('Webhook').item.json.body, null, 2) }}")
time.sleep(1)
page.screenshot(path='/private/tmp/n28.png')
