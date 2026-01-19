from aiogram import Router, F
from aiogram import types

from database import supabase

from keyboards import inline_builder
from keyboards import keyboard

from utils import KeyboardPaginator, get_project_root

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from aiogram.filters import or_f

router = Router()

@router.callback_query(F.data == "help")
async def info(query: types.CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="« Menu", callback_data="menu")
    pattern = {
        "caption": (
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
        ),
        "reply_markup": keyboard.as_markup(),
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data == "menu")
async def menu(query: types.CallbackQuery, isAdmin: bool):
    
    kb = keyboard.inlineKb(isAdmin)
    await query.message.edit_caption(caption="", reply_markup=kb)
    await query.answer()

@router.callback_query(F.data == 'cancel')
async def cancel(query: types.CallbackQuery, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await query.message.answer_photo(photo=types.FSInputFile(path=photo), caption='', reply_markup=inline_builder(text='« Menu', callback_data='menu'))

@router.callback_query(F.data == "delete")
async def delete(query: types.CallbackQuery):
    await query.message.delete()

@router.callback_query(F.data == "subjects")
async def subjects(query: types.CallbackQuery):
    response = await supabase.get_subjects()
    subjects = response.data
    text = []
    callback = []
    for subject in subjects:
        text.append(subject['title'])
        callback.append('subject_'+subject['slug'])
    text.append('« Menu')
    callback.append('menu')
    pattern = {
        "caption": (
            "<b>📚 Subjects</b>\n"
        ),
        "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data == "mocks")
async def mocks(query: types.CallbackQuery):
    response = await supabase.get_subjects()
    subjects = response.data
    text = []
    callback = []
    for subject in subjects:
        text.append(subject['title'])
        callback.append('mocks_'+subject['slug'])
    text.append('« Menu')
    callback.append('menu')
    pattern = {
        "caption": (
            "<b>📄 Mocks</b>\n"
            "\n"
            "Choose subject to get mocks for"
        ),
        "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('mocks_'))
async def mocksSubject(query: types.CallbackQuery):
    response = await supabase.get_mocks(query.data.split(sep="_", maxsplit=1)[1])
    mocks = response.data
    buttons = []
    for mock in mocks:
        buttons.append({'text':mock['title'], 'callback_data': 'mock_'+str(mock['id'])})
    additional_buttons = [
        [
            types.InlineKeyboardButton(text='« Menu', callback_data="mocks"),
        ],
    ]
    paginator = KeyboardPaginator(
        data=buttons,
        router=router,
        per_page=5,
        per_row=1,
        additional_buttons=additional_buttons
    )
    pattern = {
        "caption": (
            "<b>📄 Mocks</b>\n"
        ),
        "reply_markup": paginator.as_markup()
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('mock_'))
async def mock(query: types.CallbackQuery):
    res1 = await supabase.get_mock(query.data.split(sep="_", maxsplit=1)[1])
    mock = res1.data[0]
    res2 = await supabase.get_subject(mock['subject'])
    subject = res2.data[0]
    # file = await supabase.get_material_file(material['filename'])
    pattern = {
        "caption": (
            "<b>"+mock['title']+"</b>\n"
            "\n"
            "📚 "+subject['title']
        ),
        "reply_markup": inline_builder(text='« Menu', callback_data='delete', sizes=1),
        "document": mock['filename']
    }
    await query.message.answer_document(**pattern)
    await query.answer()

@router.callback_query(F.data == "materials")
async def materials(query: types.CallbackQuery):
    response = await supabase.get_subjects()
    subjects = response.data
    text = []
    callback = []
    for subject in subjects:
        text.append(subject['title'])
        callback.append('materials_'+subject['slug'])
    text.append('« Menu')
    callback.append('menu')
    pattern = {
        "caption": (
            "<b>📖 Materials</b>\n"
            "\n"
            "Choose subject to get materials for"
        ),
        "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('materials_'))
async def materialsSubject(query: types.CallbackQuery):
    response = await supabase.get_materials(query.data.split(sep="_", maxsplit=1)[1])
    materials = response.data
    buttons = []
    for material in materials:
        buttons.append({'text':material['title'], 'callback_data': 'material_'+str(material['id'])})
    additional_buttons = [
        [
            types.InlineKeyboardButton(text='« Menu', callback_data="materials"),
        ],
    ]
    paginator = KeyboardPaginator(
        data=buttons,
        router=router,
        per_page=5,
        per_row=1,
        additional_buttons=additional_buttons
    )
    pattern = {
        "caption": (
            "<b>📖 Materials</b>\n"
        ),
        "reply_markup": paginator.as_markup()
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('material_'))
async def material(query: types.CallbackQuery):
    res1 = await supabase.get_material(query.data.split(sep="_", maxsplit=1)[1])
    material = res1.data[0]
    res2 = await supabase.get_subject(material['subject'])
    subject = res2.data[0]
    # file = await supabase.get_material_file(material['filename'])
    pattern = {
        "caption": (
            "<b>"+material['title']+"</b>\n"
            "\n"
            "📚 "+subject['title']
        ),
        "reply_markup": inline_builder(text='« Menu', callback_data='delete', sizes=1),
        "photo": material['filename']
    }
    await query.message.answer_photo(**pattern)
    await query.answer()

@router.callback_query(F.data.startswith('subject_'))
async def subject(query: types.CallbackQuery):
    response = await supabase.get_subject(query.data.split(sep="_", maxsplit=1)[1])
    subject = response.data[0]
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="« Menu", callback_data="subjects")
    pattern = {
        "caption": (
            f"<b>📚 {subject['title']}</b>\n"
            "\n"
            f"{subject['description']}"
        ),
        "reply_markup": keyboard.as_markup(),
    }
    await query.message.edit_caption(**pattern)
    await query.answer()