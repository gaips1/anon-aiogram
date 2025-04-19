from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
import database.models.users as db_users
from middlewares import GetUserMiddleware
import routers.auth as auth
from aiogram.utils.deep_linking import create_start_link
from routers.forwards import prepare_forward
from aiogram.fsm.context import FSMContext

router = Router()
router.message.middleware(GetUserMiddleware())

@router.message(Command("start"))
async def start_handler(message: Message, command: CommandObject, user: db_users.User | None, state: FSMContext):
    if not user:
        return await auth.register(message, user)
    
    link = await create_start_link(message.bot, user.message_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Переслать", url="tg://msg_url?url="+link)],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
    ])

    if command.args:
        if command.args == user.message_id:
            return await message.answer("Вы не можете отправить сообщение самому себе!")
        
        return await prepare_forward(message, user, command.args, state)
    
    return await message.answer(
        f"🔗 Вот твоя личная ссылка:\n{link}\nОпубликуй её и получай анонимные сообщения",
        reply_markup=kb
    )