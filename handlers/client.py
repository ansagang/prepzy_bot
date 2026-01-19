from aiogram import Router, F, types
from aiogram.filters import Command, or_f


from keyboards import keyboard, inline_builder

from utils import get_project_root
from database import supabase

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
        "<b>Commands:</b>\n"
        "\n"
        "<b>How to open menu ❓</b>\n"
        "• Use command /start or just write Menu in the chat\n"
        "\n"
        "<b>What this bot helps with ❓</b>\n"
        "• Use command /info or just write Info in the chat\n"
        "\n"
        "<b>How to get random material ❓</b>\n"
        "• Use command /random_material\n"
        "\n"
        "<b>How to get random mock ❓</b>\n"
        "• Use command /random_mock\n"
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

@router.message(Command('random_material'))
async def random_material(message: types.Message):
    material = await supabase.get_random_material()
    pattern = {}
    pattern['reply_markup'] = inline_builder(text='« Menu', callback_data='delete', sizes=1)
    pattern['chat_id'] = message.from_user.id
    if material:
        response = await supabase.get_subject(material['subject'])
        subject = response.data[0]
        pattern['caption'] = (
            "<b>"+material['title']+"</b>\n"
            "\n"
            "📚 "+subject['title']
        )
        pattern['photo'] = material['filename']
        await message.bot.send_photo(**pattern)
    else:
        pattern['text'] = (
            "<b>No materials available</b>"
        )
        await message.bot.send_message(**pattern)
    await message.delete()

@router.message(Command('random_mock'))
async def random_mock(message: types.Message):
    mock = await supabase.get_random_mock()
    pattern = {}
    pattern['reply_markup'] = inline_builder(text='« Menu', callback_data='delete', sizes=1)
    pattern['chat_id'] = message.from_user.id
    if mock:
        response = await supabase.get_subject(mock['subject'])
        subject = response.data[0]
        pattern['caption'] = (
            "<b>"+mock['title']+"</b>\n"
            "\n"
            "📚 "+subject['title']
        )
        pattern['document'] = mock['filename']
        await message.bot.send_document(**pattern)
    else:
        pattern['text'] = (
            "<b>No mocks available</b>"
        )
        await message.bot.send_message(**pattern)
    await message.delete()