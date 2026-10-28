ta = page.locator('[data-test-id="parameter-input-text"] textarea').first
ta.fill('Ты помогаешь администратору компьютера. Агент-сторож прислал событие в формате JSON. Объясни по-русски в двух-трёх предложениях, что произошло и нужно ли что-то делать.\n\nСобытие: {{ JSON.stringify($json.body) }}')
time.sleep(2); page.locator('text=Source for Prompt').first.click(); time.sleep(2)
page.screenshot(path='/private/tmp/n14.png')
