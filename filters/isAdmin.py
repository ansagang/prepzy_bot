from aiogram import types
from aiogram.filters import BaseFilter

import config

class IsAdmin(BaseFilter):

    async def __call__(self, query_or_message: types.CallbackQuery | types.Message):
        try:
            return query_or_message.from_user.id in config.admin
        except:
            return False