from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

import config

class CheckAdmin(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: CallbackQuery | Message, data: Dict[str, Any]) -> Any:
        
        def checkAdmin():
            if event.from_user.id in config.admin:
                return True
            else:
                return False
        data['isAdmin'] = checkAdmin()

        return await handler(event, data)