import asyncio
import logging
import sys
import random
from uuid import uuid4

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold, hlink
from apscheduler.util import check_callable_args

from conf.config import settings
from bpower import get_in_stock_products, main2
from apscheduler.schedulers.asyncio import AsyncIOScheduler

dp = Dispatcher()

builder = InlineKeyboardBuilder()

scheduler = AsyncIOScheduler()

bot = None  # оголошуємо глобальну змінну bot

# Список повідомлень для випадкового вибору
messages = [
    "Привіт!",
    "Як справи?",
    "Гарного дня!",
    "Що нового?",
    "Як ваше здоров'я?"
]

MY_COMMAND = "sch"


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    # for index in range(1, 5):
    #     builder.button(text=f"Set {index}", callback_data=f"set:{index}")
    builder.button(text=f"В наявності", callback_data=f"set:1")
    builder.button(text=f"Очікуються", callback_data=f"set:2")

    await message.answer("Вибери що хочеш", reply_markup=builder.as_markup())


@dp.message(Command(MY_COMMAND))
async def schedule_message_handler(message: types.Message):
    await message.reply("Привіт! Я бот, який надсилає повідомлення.")
    # Передаємо bot як аргумент через kwargs
    job = scheduler.add_job(send_random_message, 'interval', hours=5,
                            kwargs={'chat_id': message.chat.id, 'bot': bot}, id=str(uuid4()))
    # Додано обробку помилок
    try:
        check_callable_args(send_random_message, [], {'chat_id': message.chat.id, 'bot': bot})
    except ValueError as e:
        await message.reply(f"Помилка додавання задачі до планувальника: {e}")


# Функція для надсилання випадкового повідомлення
async def send_random_message(chat_id: int, bot: Bot):  # Додаємо bot як аргумент

    products = main2()
    if products:
        for row in products:
            card = f"{hlink(row.get('title'), row.get('link'))}\n" \
                   f"{hbold('Прайс: ')} {row.get('price')}\n" \

            await bot.send_message(chat_id, card)
    else:
        await bot.send_message(chat_id, 'Немає змін по аккумуляторах')
    # random_message = random.choice(messages)
    # await bot.send_message(chat_id, random_message)


@dp.callback_query(lambda c: c.data.startswith("set:"))
async def process_callback_set(callback_query: CallbackQuery) -> None:
    # await callback_query.message.edit_text(f"Почекай трохи...")
    await callback_query.answer("Почекай трохи...")
    """
    This handler processes the callback data from the buttons
    """
    # Extract the value from the callback data
    action = callback_query.data.split(":")[1]  # Get the number after "set:"

    # Respond based on the action
    if action == "1":
        await callback_query.answer("В наявності: Товари в наявності.")

        for row in get_in_stock_products():
            card = f"{hlink(row.get('title'), row.get('link'))}\n" \
                   f"{hbold('Прайс: ')} {row.get('price')}\n" \

            await callback_query.message.answer(card)
    elif action == "2":
        await callback_query.answer("Очікуються: Товари, які очікуються.")

    # Optionally, you can edit the message or send a new one
    await callback_query.message.edit_text(f"Ви вибрали: {action}")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")

#
# async def main() -> None:
#     # Initialize Bot instance with default bot properties which will be passed to all API calls
#     global bot  # оголошуємо глобальну змінну bot
#     bot = Bot(token=settings.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
#
#     # And the run events dispatching
#     await dp.start_polling(bot, on_startup=on_startup)


async def main() -> None:
    global bot
    bot = Bot(token=settings.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    scheduler.start()   # Переміщено сюди
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

