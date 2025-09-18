from aiogram import types, Dispatcher, Bot, F
from aiogram.filters import CommandObject, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import arrow
import logging
import asyncio
import config
import json

##################################################################################################################

moduls = 0

try:
    import moduls.db as dbm
    moduls += 1
except:
    print('Ошибка загрузки db_module')

# try:
#     import moduls.schedule.schedule as sm
#     moduls += 1
# except:
#     print('Ошибка загрузки schedule_module')

# try:
#     import moduls.schedule.schedule_manager as smn
#     moduls += 1
# except:
#     print('Ошибка загрузки schedule_manager')

try:
    import moduls.time as tm
    moduls += 1
except:
    print('Ошибка загрузки time_module')

# try:
#     import moduls.task as taskm
#     moduls += 1
# except:
#     print('Ошибка загрузки task_module')

print(f'Модулей установлено: {moduls}')

##################################################################################################################

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

admins = [134132306, 5207843376]

##################################################################################################################

try:
    with open(r"./settings/schedule.json", "r", encoding="utf_8_sig") as f:
        schedule = json.loads(f.read())
except:
    print('Не удалось загрузить расписание')

try:
    with open(r"./settings/addresses.json", "r", encoding="utf_8_sig") as f:
        adresses = json.loads(f.read())
except:
    print('Не удалось загрузить адреса')

try:
    with open(r"./settings/localization.json", "r", encoding="utf_8_sig") as f:
        localization = json.loads(f.read())
except:
    print('Не удалось загрузить локализацию')

##################################################################################################################

@dp.message(CommandStart(deep_link=True))
async def link(message: types.Message, command: CommandObject):
    print("Рефералка")

@dp.message(CommandStart())
async def start(message: types.Message):
    db_user_id = await dbm.check_user(message.from_user.id)
    group = await dbm.settings_manager(db_user_id, 'check')

    buttons = InlineKeyboardBuilder()
    if group != None and group != '-1':
        buttons.row(InlineKeyboardButton(text = localization['normal']['buttons']['schedule'], callback_data = f'schedule_{group}'))
        buttons.row(InlineKeyboardButton(text = localization['normal']['buttons']['alarms'], callback_data = f'alarms_{group}'))
        text = localization['normal']['hello']['base']
    elif group == '-1':
        buttons.row(InlineKeyboardButton(text = 'Окак', callback_data = f'back'))
        text = localization['normal']['hello']['terminate']
    else:
        for group in schedule.keys():
            buttons.row(InlineKeyboardButton(text = group, callback_data = f'alarms_{group}'))
        text = localization['normal']['hello']['registarate']

    await message.answer(text, parse_mode = "Markdown", reply_markup = buttons.as_markup())

@dp.callback_query(F.data[:6] == 'alarms')
async def buttons_manager(callback: types.CallbackQuery):
    db_user_id = await dbm.check_user(callback.from_user.id)

    cs = str(callback.data).split('_')
    buttons = InlineKeyboardBuilder()

    if len(cs) == 2 and cs[1] != 'None':
        buttons.row(InlineKeyboardButton(text = localization['normal']['buttons']['yes'], callback_data = f'alarms_{cs[1]}_yes'))
        buttons.row(InlineKeyboardButton(text = localization['normal']['buttons']['no'], callback_data = f'alarms_{cs[1]}_no'))
        text = localization['normal']['alarms']['quest']
    elif len(cs) == 3:
        if cs[2] == 'yes':
            state = 1
            text = localization['normal']['alarms']['ans_yes']
        elif cs[2] == 'no':
            state = 0
            text = localization['normal']['alarms']['ans_no']

        await dbm.settings_manager(db_user_id, 'add', cs[1], state)
        buttons.row(InlineKeyboardButton(text = localization['normal']['buttons']['ok'], callback_data = f'back'))

    await callback.message.edit_text(text, parse_mode = "Markdown", reply_markup = buttons.as_markup())

@dp.callback_query(F.data[:8] == 'schedule')
async def buttons_manager(callback: types.CallbackQuery):
    db_user_id = await dbm.check_user(callback.from_user.id)

    cs = str(callback.data).split('_')
    buttons = InlineKeyboardBuilder()

    if len(cs) == 2 and cs[1] != 'None':
        if await tm.this_day(1) == 'ПН':
            week = 'next'
        else:
            week = 'now'
        
        buttons.row(InlineKeyboardButton(text = '⏪', callback_data = f'schedule_{cs[1]}_back'), InlineKeyboardButton(text = 'Назад', callback_data = f'back'), InlineKeyboardButton(text = '⏩', callback_data = f'schedule_{cs[1]}_next'))

        text = f'{await tm.this_day()} - {await tm.week_color(week)}\n\n'
        for num in schedule[cs[1]][await tm.this_day()].keys():
            room = str(schedule[cs[1]][await tm.this_day()][num][await tm.week_color('now')]['room'])
            split_room = str(schedule[cs[1]][await tm.this_day()][num][await tm.week_color('now')]['room']).split('-')
            try:
                for housing in adresses.keys():
                    for flor in adresses[housing]:
                        if len(split_room) == 1:
                            if int(room) > int(adresses[housing][flor]["min"]) and int(room) < int(adresses[housing][flor]["max"]):
                                adres = housing
                        else:
                            if split_room[0] in housing:
                                adres = housing
            except:
                adres = ''

            text += f'{num}-я пара {schedule[cs[1]][await tm.this_day()][num]['time']['start']} - {schedule[cs[1]][await tm.this_day()][num]['time']['end']}\n{schedule[cs[1]][await tm.this_day()][num][await tm.week_color(week)]['title']}\n{schedule[cs[1]][await tm.this_day()][num][await tm.week_color(week)]['teacher']}\n{adres} {room} {schedule[cs[1]][await tm.this_day()][num][await tm.week_color(week)]['type']}\n\n'
    else:
        buttons.row(InlineKeyboardButton(text = 'Ок', callback_data = f'back'))
        text = 'В разработке...'
    await callback.message.edit_text(text, parse_mode = "Markdown", reply_markup = buttons.as_markup())

@dp.callback_query(F.data == 'back')
async def buttons_manager(callback: types.CallbackQuery):
    db_user_id = await dbm.check_user(callback.from_user.id)
    group = await dbm.settings_manager(db_user_id, 'check')

    buttons = InlineKeyboardBuilder()
    if group != None and group != '-1':
        buttons.row(InlineKeyboardButton(text = localization['normal']['buttons']['schedule'], callback_data = f'schedule_{group}'))
        buttons.row(InlineKeyboardButton(text = localization['normal']['buttons']['alarms'], callback_data = f'alarms_{group}'))
        text = localization['normal']['hello']['base']
    elif group == '-1':
        buttons.row(InlineKeyboardButton(text = 'Окак', callback_data = f'back'))
        text = localization['normal']['hello']['terminate']
    else:
        for group in schedule.keys():
            buttons.row(InlineKeyboardButton(text = group, callback_data = f'alarms_{group}'))
        text = localization['normal']['hello']['registarate']

    await callback.message.edit_text(text, parse_mode = "Markdown", reply_markup = buttons.as_markup())

@dp.callback_query(F.data == 'ok')
async def buttons_manager(callback: types.CallbackQuery):
    await callback.message.edit_text('Не забудь!', parse_mode = "Markdown")
    await asyncio.sleep(0.5)
    await callback.message.delete()

@dp.message()
async def dell_user_massage(message: types.Message):
    await message.delete()

async def safe_daily_message(bot, group, num):
    try:
        users = await dbm.users_on_alarms(group)
        try:
            room = str(schedule[group][await tm.this_day()][str(int(num) + 1)][await tm.week_color('now')]['room'])
            split_room = str(schedule[group][await tm.this_day()][str(int(num) + 1)][await tm.week_color('now')]['room']).split('')
            type = schedule[group][await tm.this_day()][str(int(num) + 1)][await tm.week_color('now')]['type']
            work = schedule[group][await tm.this_day()][str(int(num) + 1)][await tm.week_color('now')]['title']
            teach = schedule[group][await tm.this_day()][str(int(num) + 1)][await tm.week_color('now')]['teacher']
        except Exception as e:
            return
        
        adres = ''

        for housing in adresses.keys():
            for flor in adresses[housing]:
                if split_room[0] != 'Л':
                    if int(room) > int(adresses[housing][flor]["min"]) and int(room) < int(adresses[housing][flor]["max"]):
                        adres = housing
                elif split_room[1] == '-':
                    if split_room[0] in housing:
                        adres = housing

        buttons = InlineKeyboardBuilder()
        buttons.row(InlineKeyboardButton(text = 'Ок', callback_data = f'ok'))
        # for user_id in users:
        await bot.send_message(5207843376, f"{adres} {room} {type}\n{work}\n{teach}", parse_mode = "Markdown", reply_markup = buttons.as_markup())
        scheduler.remove_job(f'alarm_{group}_{schedule[group][await tm.this_day()][str(int(num) + 1)]['time']['end']}')

    except Exception as e:
        print(e)

async def setup_scheduler(bot):
    for group in schedule.keys():
        for num in schedule[group][await tm.this_day()].keys():
            if num != len(schedule[group][await tm.this_day()]):
                time = schedule[group][await tm.this_day()][num]['time']['end']
                hour, minute = map(int, time.split(':'))

                scheduler.add_job(
                    safe_daily_message,
                    CronTrigger(hour=hour, minute=minute),
                    id=f'alarm_{group}_{time}',
                    args=[bot, group, num]
                )

async def main():
    scheduler.add_job(
        setup_scheduler,
        CronTrigger(hour=8, minute=46),
        id=f'alarms',
        args=[bot]
    )

    await setup_scheduler(bot)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())