from typing import Annotated, List, Any

import aiogram
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

if aiogram.__version__ >= "3.0.0b8":
    from pydantic.v1 import Field
else:
    from pydantic import Field

from ._base import BasePaginator


class KeyboardPaginator(BasePaginator):
    """Allows to create a new markup with keyboard pagination"""

    def __init__(
        self,
        data: Annotated[List[Any], Field(min_items=1)],
        router: Router,
        additional_buttons: List[Any] = list(),
        pagination_buttons: List[Any] = ["⏪", "⬅️", "➡️", "⏩"],
        per_page: int = 2,
        per_row: int = 1,
    ):
        """
        :param data - buttons data. (`required`)
        >>> data = [
            {
                "text": "Button name",
                "callback_data": "callback_data",
            },
            InlineKeyboardButton(
                text="Button name 2", callback_data="callback_data_2"
            ),
            {
                "text": "Button name 999",
                "callback_data": "callback_data_999",
            },
        ]

        :param router: pagination automatization. (`required`)
        :param additional_buttons: provide additional buttons, that will be inserted after pagination panel. `(default=None)`
        :param pagination_key: custom callback data, which will be attached to the callback of each pagination button
        :param pagination_buttons: list of `four` buttons, where each is a string or None (if you don't want to add this button) `(default=["⏪", "⬅️", "➡️", "⏩"])`
        :param per_row: amount of items per row `(default=8)`
        :param per_page: amount of items per page `(default=10)`
        """
        if isinstance(per_row, int):
            per_row = (per_row,)

        self.per_row = per_row

        super().__init__(
            data=data,
            router=router,
            additional_buttons=additional_buttons,
            pagination_buttons=pagination_buttons,
            per_page=per_page,
        )

    def _build(self):
        self.builder = InlineKeyboardBuilder()

        for button in self._current_data_chunk:
            button = self._format_button(button)
            self.builder.add(button)

        self.builder.adjust(*self.per_row)

        self._build_pagination_buttons(self.builder)

    async def _callback_handler(self, call: CallbackQuery):
        self.current_page_index = int(call.data.split("|")[-1])
        self._build()

        await call.message.edit_reply_markup(reply_markup=self.as_markup())