import random
import string
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
import database.models.users as db_users
from middlewares import GetUserMiddleware
from aiogram import Router, F

router = Router()
router.message.middleware(GetUserMiddleware())

async def generate_unique_id():
    while True:
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        result = await db_users.get_user_by_message_id(id)
        if result is None:
            return id

async def register(message: Message, user: db_users.User):
    kb = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
    ]], resize_keyboard=True, one_time_keyboard=True)

    await message.answer("🔗 Для использования бота докажите, что вы не робот, отправив свой номер телефона", reply_markup=kb)

@router.message(F.contact)
async def handle_contact(message: Message, user: db_users.User):
    if user: return
    
    user = await db_users.create_user(
        id=message.from_user.id,
        number=message.contact.phone_number,
        message_id=await generate_unique_id(),
        is_admin=False
    )

    await message.answer("✅ Вы успешно подтвердили свою личность!")
    return await message.reply_to_message.delete()