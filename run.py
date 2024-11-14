import asyncio
import logging
import aiosqlite
import datetime
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message , ReplyKeyboardMarkup, KeyboardButton,ContentType
from config import TOKEN


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()


main_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        (KeyboardButton(text='Отправить контакт', request_contact=True))
    ]
])


@dp.message(CommandStart())
async def Start(message: Message):
    await message.answer('Отправьте в этот бот нужный контакт через кнопку поделиться контактом', reply_markup=main_kb)
    telegram_id = message.from_user.id
    name = message.from_user.first_name
    await Add_to_base(telegram_id, name)

@dp.message(F.contact)
async def handle_contact(message: Message):
    contact = message.contact
    phone_number = contact.phone_number
    await message.answer(f'Номер телефона : {phone_number}')


async def Add_to_base(telegram_id, name):
    async with aiosqlite.connect('Telebase.db') as db:     
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, name TEXT, date TEXT) ")
        cursor = await db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        date = await cursor.fetchone()
        if date is not None:
            return
    date = f'{datetime.date.today()}'
    async with aiosqlite.connect('Telebase.db') as db:
        await db.execute("INSERT INTO users (telegram_id, name, date) VALUES (?, ?, ?)",
                                                            (telegram_id, name, date))
        await db.commit()


@dp.message(Command('del'))
async def Remove_kb(message: Message):
    await message.answer('Клавиатура успешно удалена ', reply_markup=types.ReplyKeyboardRemove())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')        
    asyncio.run(main())