import json
import moduls.time as tm

with open(r"C:\Users\Misha\Documents\Yandex.Disk\Проект\schedule.json", "r", encoding="utf_8_sig") as f:
    schedule = json.loads(f.read())

async def schedule_per_day(group:str, day_of_week:str ,lesson_number:int, week_color:str):
    if not lesson_number:
        lesson_number = await tm.what_a_lesson(group, schedule)

    if not day_of_week:
        day_of_week = await tm.this_day()

    if not week_color:
        week_color = await tm.week_color('now')

    try:
        gl = schedule[group][day_of_week][lesson_number]
    except Exception as e:
        if str(e) == f"'{group}'":
            print(1)
        elif str(e) == f"'{day_of_week}'":
            print(2)
        elif str(e) == f"'{lesson_number}'":
            print(3)

    time = gl['time']
    lesson = gl[week_color]