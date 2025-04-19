from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import database.models.users as db_users
from middlewares import GetUserMiddleware
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
import database.models.users as db_users
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

class ForwardState(StatesGroup):
    forward = State()

cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_forward")]
    ])

async def prepare_forward(message: Message, user: db_users.User | None, message_id: str, state: FSMContext):
    forward_to_user = await db_users.get_user_by_message_id(message_id)
    if not forward_to_user:
        return await message.answer("Пользователь не найден!")
    
    if user == forward_to_user:
        return await message.answer("Вы не можете отправить сообщение самому себе!")
    
    await state.set_state(ForwardState.forward)
    await state.update_data(forward_to_user=forward_to_user)

    return await message.answer(
        "🚀 Здесь можно отправить анонимное сообщение человеку, который опубликовал эту ссылку.\n\nНапишите сюда всё, что хотите ему передать, и через несколько секунд он получит ваше сообщение, но не будет знать от кого.\n\nОтправить можно фото, видео, 💬 текст, 🔊 голосовые, 📷видеосообщения (кружки), гифки, а также стикеры.\n\n⚠️ Это полностью анонимно!",
        reply_markup=cancel_kb
    )

@router.callback_query(F.data == "cancel_forward", ForwardState.forward)
async def cancel_forward(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    return await callback.message.edit_text("❌ Отправка отменена!", reply_markup=None)

@router.callback_query(F.data.startswith("forward/"))
async def forward_callback(callback: CallbackQuery, user: db_users.User, state: FSMContext):
    await callback.answer()
    message_id = callback.data.split("/")[1]
    return await prepare_forward(callback.message, user, message_id, state)

@router.message(ForwardState.forward, F.text)
async def send_forward(message: Message, user: db_users.User, state: FSMContext):
    data = await state.get_data()
    forward_to_user: db_users.User = data.get("forward_to_user")

    await state.clear()
    
    if not forward_to_user:
        return await message.answer("Произошла ошибка!")
    
    msg = await message.bot.send_message(
        forward_to_user.id,
        "📨 Получено новое сообщение" if not forward_to_user.is_admin else f"📨 Получено новое сообщение \n\nимя: {message.from_user.full_name} айди: {message.from_user.id} юзернаме: @{message.from_user.username} номер {user.number}",
        disable_notification=True
    )
    
    await message.copy_to(forward_to_user.id, reply_to_message_id=msg.message_id, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔁 Ответить", callback_data="forward/"+user.message_id)
    ]]))

    await message.answer("✅ Сообщение успешно отправлено!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔁 Отправить ещё", callback_data="forward/"+forward_to_user.message_id),
    ]]))

    await user.update(sended_messages=user.sended_messages+1)
    await forward_to_user.update(getted_messages=forward_to_user.getted_messages+1)

    await message.delete()
    await message.bot.delete_message(message.chat.id, message.message_id-1)