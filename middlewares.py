from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
import database.models.users as users

class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = await users.get_user_by_id(event.from_user.id)
        data['user'] = user
        
        if user and user.is_banned:
            return await event.answer("Вы заблокированы администратором этого бота!\nТехническая поддержка - @gaips")
        
        return await handler(event, data)