from aiogram import Router, F, types
from aiogram.filters import Command, or_f


from keyboards import keyboard, inline_builder

from utils import get_project_root

# from filters import IsChannel

router = Router()

@router.message(or_f(Command('start'), F.text == "Menu"))
async def menu_cmd(message: types.Message, isAdmin: bool):
    filename = get_project_root('assets/logo.png')
    kb = keyboard.inlineKb(isAdmin)
    await message.bot.send_photo(chat_id=message.from_user.id, photo=types.FSInputFile(path=filename), caption='', reply_markup=kb)
    await message.delete()

@router.message(or_f(Command('help'), F.text == "Commands"))
async def help_cmd(message: types.Message):
    filename = get_project_root('assets/logo.png')
    caption = (
        "Commands:\n"
        "\n"
        "<b>How to open menu ❓</b>\n"
        "• Use command /start or just write Menu in the chat\n"
        "\n"
        "<b>Bot information</b>\n"
        "• Use command /info or just write Info in the chat\n"
        "\n"
        "<b>How to start practice test ❓</b>\n"
        "• Use command /practice\n"
    )
    await message.bot.send_photo(chat_id=message.from_user.id, photo=types.FSInputFile(path=filename), caption=caption, reply_markup=inline_builder(text='« Назад', callback_data='delete'))
    await message.delete()

@router.message(or_f(Command('info'), F.text == "Info"))
async def info_cmd(message: types.Message):
    filename = get_project_root('assets/logo.png')
    caption = (
        "🌱 I am multifunctional, advanced, and convenient telegram bot for preparing to such exams as IELTS, SAT and etc.\n"
        "\n"
        "<b>My creator:</b>\n"
        "-@ansagang \n"
    )
    await message.bot.send_photo(chat_id=message.from_user.id, photo=types.FSInputFile(path=filename), caption=caption, reply_markup=inline_builder(text='« Назад', callback_data='delete'))
    await message.delete()