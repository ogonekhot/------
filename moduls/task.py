import asyncio
from aiogram import Bot, Dispatcher, types
import arrow

async def alarm(bot: Bot, user_id: int, message_text: str, target_time:str):
    delay_seconds = max(0, (arrow.now().replace(hours=target_time.split(':')[0], minutes = target_time.split(':')[1] - 10) - arrow.now()).total_seconds())

    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)
        try:
            await bot.send_message(user_id, message_text)
        except Exception as e:
            print(f"Ошибка отправки: {e}")

# async def send_scheduled_message_non_blocking(bot: Bot, user_id: int, message_text: str, ):
#     now = arrow.now()
#     delay_seconds = max(0, (target_time - now).total_seconds())
    
#     if delay_seconds > 0:
#         await asyncio.sleep(delay_seconds)
#         try:
#             await bot.send_message(user_id, message_text)
#         except Exception as e:
#             print(f"Ошибка отправки: {e}")

# # Обработчик команды
# @dp.message_handler(commands=['remind'])
# async def schedule_reminder(message: types.Message):
#     try:
#         # Парсим время из сообщения (формат: /remind 15:30 Сделать что-то)
#         time_str, *text_parts = message.text.split()[1:]
#         reminder_text = ' '.join(text_parts)
        
#         # Создаем время напоминания
#         target_time = arrow.now().replace(
#             hour=int(time_str.split(':')[0]),
#             minute=int(time_str.split(':')[1]),
#             second=0
#         )
        
#         # Запускаем в фоне без блокировки
#         asyncio.create_task(
#             send_scheduled_message_non_blocking(
#                 bot, message.from_user.id, reminder_text, target_time
#             )
#         )
        
#         await message.answer(f"✅ Напоминание установлено на {target_time.format('HH:mm')}")
        
#     except (IndexError, ValueError):
#         await message.answer("Используйте: /remind HH:MM текст_напоминания")