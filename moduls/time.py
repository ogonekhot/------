import arrow

async def this_day(next:int = 0):
    day = arrow.now().weekday() + next

    weekday = 'None'

    if day == 0:
        weekday = 'ПН'
    elif day == 1:
        weekday = 'ВТ'
    elif day == 2:
        weekday = 'СР'
    elif day == 3:
        weekday = 'ЧТ'
    elif day == 4:
        weekday = 'ПТ'
    elif day == 5:
        weekday = 'СБ'
    elif day == 6:
        weekday = 'ВС'
    else:
        weekday = 'ПН'

    return weekday

async def what_a_lesson(group, schedule):
    weekday = await this_day()
    time = arrow.now().time()

    for i in schedule[group][weekday].keys():
        stime = str(schedule[group][weekday][i]['time']['start']).split(':')
        etime = str(schedule[group][weekday][i]['time']['end']).split(':')

        start = arrow.now().replace(hour=int(stime[0]), minute=int(stime[1])).time()
        end = arrow.now().replace(hour=int(etime[0]), minute=int(etime[1])).time()

        if time < start and i == 1:
            return f'before_{i}'
        elif time < end and time > start:
            return f'now_{i}'
        elif time > end and i == len(schedule[group][weekday].keys()):
            return f'next_{i}'


async def week_color(how):
    reference_date = arrow.now().replace(month = 9, day = 4, year = 2025)
    reference_week = 'Белая неделя'

    weeks_diff = (arrow.now().floor('week') - reference_date.floor('week')).days // 7

    if weeks_diff % 2 == 0:
        week = reference_week
    else:
        week = 'Зелёная неделя' if reference_week == 'Белая неделя' else 'Белая неделя'

    if how == 'now':
        return week
    elif how == 'next':
        if week == 'Белая неделя':
            return 'Зелёная неделя'
        else:
            return 'Белая неделя'
    
async def ost(group, lesson, schedule):
        weekday = await this_day()
        etime = str(schedule[group][weekday][lesson]['time']['end']).split(':')

        end = arrow.now().replace(hour=int(etime[0]) - arrow.now().time().hour, minute=int(etime[1])  - arrow.now().time().minute).format('HH:mm')
        return end