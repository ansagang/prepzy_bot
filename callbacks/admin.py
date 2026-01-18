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
            "Choose data to add:"
        ),
        "reply_markup": inline_builder(text=['Add subject', 'Add material', 'Add mock', 'Add practice', '« Menu'], callback_data=['add_subject', 'add_material', 'add_mock', 'add_practice', 'menu'])
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('add')))
async def add_subject(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'add_subject':
        await query.message.answer('Enter the title', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
        await state.set_state(FMSsubjects.title)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSsubjects.title))
async def add_subject_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.update_data(slug=slugify(message.text))
    await message.answer('Enter the description', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSsubjects.description)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSsubjects.description))
async def add_subject_final(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(description=message.text)
    await supabase.add_subject(state)
    await state.clear()
    await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Subject has been added successfully', reply_markup=inline_builder(text='« Menu', callback_data='menu'))

@router.callback_query(and_f(F.data == "delete_", IsAdmin()))
async def delete(query: types.CallbackQuery):
    pattern = {
        "caption": (
            "<b>❌ Delete</b>\n"
            "\n"
            "Choose data to delete:"
        ),
        "reply_markup": inline_builder(text=['Delete subject', 'Delete material', 'Delete mock', 'Delete practice', '« Menu'], callback_data=['delete_subject', 'delete_material', 'delete_mock', 'delete_practice', 'menu'])
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_subject-')))
async def delete_subject(query: types.CallbackQuery):
    await supabase.delete_subject(query.data.split(sep='-', maxsplit=1)[1])
    caption = (
        "<b>Subject has been deleted successfully</b>"
    )
    await query.message.edit_caption(caption=caption, reply_markup=inline_builder(text=['« Menu'], callback_data=['delete_subject']))
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith("delete")))
async def delete_data(query: types.CallbackQuery):
    pattern = {}
    if query.data == 'delete_subject':
        response = await supabase.get_subjects()
        subjects = response.data
        buttons = []
        pattern['caption'] = (
            "<b>❌ Delete subject</b>\n"
            "\n"
            "Choose subject to delete"
        )
        buttons = []
        for subject in subjects:
            buttons.append({'text':subject['title'], 'callback_data':'delete_subject-'+subject['slug']})
        additional_buttons = [
            [
                types.InlineKeyboardButton(text='« Menu', callback_data="delete_"),
            ],
        ]
        paginator = KeyboardPaginator(
            data=buttons,
            router=router,
            per_page=5,
            per_row=1,
            additional_buttons=additional_buttons
        )
        pattern['reply_markup'] = paginator.as_markup()
        await query.message.edit_caption(**pattern)
        await query.answer()