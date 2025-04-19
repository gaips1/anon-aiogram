from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import database.models.users as db_users
from middlewares import GetUserMiddleware

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

def get_stats(user: db_users.User):
    return  f"<b>📊 Статистика твоей ссылки\n\n💬 Получено сообщений: {user.getted_messages}\n📨 Отправлено сообщений: {user.sended_messages}</b>\n\n😉 Распространяй ссылку и получай больше анонимных сообщений."

@router.message(Command('stats'))
async def get_stats_command(message: Message, user: db_users.User):
    return await message.answer(get_stats(user))

@router.callback_query(F.data == "stats")
async def get_stats_callback(callback: CallbackQuery, user: db_users.User):
    await callback.answer()
    return await callback.message.answer(get_stats(user))