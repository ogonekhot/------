from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import bleach
import json

schedule = {}

async def create_schedule():
    global schedule
    with open(r".\moduls\settings.json", "r", encoding="utf_8_sig") as f:
        settings = json.loads(f.read())

    for i in settings['accounts'].keys():
        group = str(i)
        schedule[group] = {}
        login = settings['accounts'][group]['login']
        password = settings['accounts'][group]['password']

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()

            await page.goto("http://lk.stu.lipetsk.ru/")
            await page.wait_for_load_state('networkidle')

            await page.fill('input[name="LOGIN"]', login)
            await page.fill('input[name="PASSWORD"]', password)
            
            await page.click('button[type="submit"]')

            await page.goto("http://lk.stu.lipetsk.ru/education/0/5:136841076/")
            await page.wait_for_load_state('networkidle')
            
            col = 0
            ajax_response = ''

            async def handle_response(response):
                nonlocal ajax_response
                nonlocal col
                if "ajax.handler.php" in response.url:
                    col += 1
                    if col == 1:
                        try:
                            body = await response.body()
                            ajax_response = body.decode('cp1251')
                        except Exception as e:
                            print(f"Ошибка при получении данных: {e}")

            page.on("response", handle_response)

            await page.reload()
            await page.wait_for_load_state('networkidle')

            weak_color = await page.query_selector('div[role=alert]')
            weak_color = await weak_color.text_content()

            await browser.close()

            soup = BeautifulSoup(ajax_response, 'html.parser')
            s = soup.find('tbody')

            for i in s.select('td'):
                clean = bleach.clean(str(i), tags=[], strip=True).strip()

                if len(clean) == 2:
                    schedule[group][clean] = {}

                if ' - ' in clean:
                    schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys())+1)] = {'time': {}, 'Белая неделя': {'title': '', 'teacher': '', 'room': '', 'type': ''}, 'Зелёная неделя': {'title': '', 'teacher': '', 'room': '', 'type': ''}}
                    schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['time']['start'] = str(clean.split(' - ')[0])
                    schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['time']['end'] = str(clean.split(' - ')[1])

                if len(str(i).split('<br/>')) == 2:
                    room = bleach.clean(str(i).split('<br/>')[0], tags=[], strip=True).strip()
                    stype = bleach.clean(str(i).split('<br/>')[1], tags=[], strip=True).strip()

                    if stype == "пр.":
                        stype = 'практика'
                    elif stype == "лек.":
                        stype = 'лекция'
                    elif stype == "лаб.":
                        stype = 'лаборатоная'

                    if schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Белая неделя']['room'] != '' and schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Белая неделя']['type'] != '':
                        schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Зелёная неделя']['room'] = str(room)
                        schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Зелёная неделя']['type'] = str(stype)
                    else:
                        schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Белая неделя']['room'] = str(room)
                        schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Белая неделя']['type'] = str(stype)

                elif 'center' in str(i):
                    title = bleach.clean(str(i).split('<br/>')[0], tags=[], strip=True).strip()
                    teacher = ''
                    if len(str(i).split('<br/>')) == 3:
                        teacher = bleach.clean(str(i).split('<br/>')[2], tags=[], strip=True).strip()

                    if schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Белая неделя']['title'] != '':
                        schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Зелёная неделя']['title'] = title
                        schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Зелёная неделя']['teacher'] = teacher
                    else:
                        schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Белая неделя']['title'] = title
                        schedule[group][list(schedule[group].keys())[-1]][str(len(schedule[group][list(schedule[group].keys())[-1]].keys()))]['Белая неделя']['teacher'] = teacher

    with open(r'C:\Users\Misha\Documents\Yandex.Disk\Проект\schedule.json', 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)


    if 'белая' in weak_color:
        return 'Белая неделя'
    else:
        return 'Зелёная неделя'