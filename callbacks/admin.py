from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types, Router, F
from aiogram.filters import and_f, or_f

from database import supabase

from slugify import slugify

from filters import IsAdmin

from utils import get_project_root, KeyboardPaginator

import config

from keyboards import inline_builder

router = Router()

class FMSsubjects(StatesGroup):
    title = State()
    slug = State()
    description = State()

@router.callback_query(and_f(F.data == "add", IsAdmin()))
async def add(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>✅ Add</b>\n"
            "\n"
            "-Choose data to add:"
        ),
        "reply_markup": inline_builder(text=['Add subject', 'Add material', 'Add mock', 'Add practice', '« Menu'], callback_data=['add_subject', 'add_material', 'add_mock', 'add_practice', 'menu'])
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('add')))
async def add(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'add_subject':
        await query.message.answer('Enter the title', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
        await state.set_state(FMSsubjects.title)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSsubjects.title))
async def add_tests_file(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.update_data(slug=slugify(message.text))
    await message.answer('Enter the description', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSsubjects.description)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSsubjects.description))
async def add_tests_subject(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(description=message.text)
    await supabase.add_subject(state)
    await state.clear()
    await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Subject has been added successfully', reply_markup=inline_builder(text='« Menu', callback_data='menu'))