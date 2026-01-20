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

class FMSmaterials(StatesGroup):
    file = State()
    subject = State()
    title = State()

class FMSmocks(StatesGroup):
    file = State()
    subject = State()
    title = State()

class FMSpractice(StatesGroup):
    slug = State()
    file = State()
    subject = State()
    answer = State()
    number = State()
    title = State()
    question = State()

class FMSquestion(StatesGroup):
    file = State()
    answer = State()
    subject = State()
    title = State()
    explanation = State()

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

@router.callback_query(and_f(IsAdmin(), FMSmaterials.subject, F.data.startswith('add_material-')))
async def add_material_subject(query: types.CallbackQuery, state: FSMContext):
    await state.update_data(subject=query.data.split(sep="-", maxsplit=1)[1])
    await query.message.answer('Send the picture', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSmaterials.file)

@router.callback_query(and_f(IsAdmin(), FMSmocks.subject, F.data.startswith('add_mock-')))
async def add_mock_subject(query: types.CallbackQuery, state: FSMContext):
    await state.update_data(subject=query.data.split(sep="-", maxsplit=1)[1])
    await query.message.answer('Send the file', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSmocks.file)

@router.callback_query(and_f(IsAdmin(), F.data.startswith('add_question-'), FMSpractice.title))
async def add_question(query: types.CallbackQuery, state: FSMContext):
    practice = await supabase.get_practice(query.data.split(sep="-", maxsplit=1)[1])
    await state.update_data(title=practice['title'])
    await state.update_data(slug=practice['slug'])
    await state.update_data(number=practice['number']+1)
    # await state.update_data(slug=slugify(query.data.split(sep="-", maxsplit=1)[1]))
    # await supabase.add_material_file(message.photo[0], message.photo[0].file_unique_id)
    await query.message.answer('Send the photo', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSpractice.file)

@router.message(and_f(IsAdmin(), FMSpractice.title))
async def add_practice(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    data_state = await state.get_data()
    subject = data_state.get('subject')
    await state.update_data(slug=slugify(message.text)+'_'+subject)
    await state.update_data(number=1)
    # await state.update_data(slug=slugify(query.data.split(sep="-", maxsplit=1)[1]))
    # await supabase.add_material_file(message.photo[0], message.photo[0].file_unique_id)
    await message.answer('Send the photo', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSpractice.file)

@router.message(and_f(IsAdmin(), F.content_type == 'photo', FMSpractice.file))
async def add_question_photo(message: types.Message, state: FSMContext):
    await state.update_data(file=message.photo[0].file_id)
    # await supabase.add_material_file(message.photo[0], message.photo[0].file_unique_id)
    await message.answer('Enter the question', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSpractice.question)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSpractice.question))
async def add_question_question(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    # await supabase.add_material_file(message.photo[0], message.photo[0].file_unique_id)
    await message.answer('Enter the answer', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSpractice.answer)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSpractice.answer))
async def add_question_answer(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    async def next(answer):
        await state.update_data(answer=answer)
        await supabase.add_practice(state)
        await state.clear()
        await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Question has been added successfully', reply_markup=inline_builder(text='« Menu', callback_data='menu'))
    if message.text == 'A':
        await next(1)
    elif message.text == 'B':
        await next(2)
    elif message.text == 'C':
        await next(3)
    elif message.text == 'D':
        await next(4)

@router.callback_query(and_f(IsAdmin(), F.data.startswith('add_practice--')))
async def add_practice_new(query: types.CallbackQuery, state: FSMContext):
    await state.update_data(subject=query.data.split(sep="--", maxsplit=1)[1])
    await query.message.answer('Enter the title', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSpractice.title)


@router.callback_query(and_f(IsAdmin(), FMSpractice.subject, F.data.startswith('add_practice-')))
async def add_practice_subject(query: types.CallbackQuery, state: FSMContext):
    pattern = {}
    await state.update_data(subject=query.data.split(sep="-", maxsplit=1)[1])
    practices = await supabase.get_practices(query.data.split(sep='-', maxsplit=1)[1])
    if len(practices) > 0:
        additional_buttons = [
            [
                types.InlineKeyboardButton(text='Create new', callback_data="add_practice--"+query.data.split(sep='-', maxsplit=1)[1]),
                types.InlineKeyboardButton(text='« Menu', callback_data="add_practice"),
            ],
        ]
        buttons = []
        pattern['caption'] = (
            "<b>✅ Add question</b>\n"
            "\n"
            "Choose practice to add question to"
        )
        buttons = []
        for practice in practices:
            buttons.append({'text':practice['title'], 'callback_data':'add_question-'+str(practice['slug'])})
        
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
        await state.set_state(FMSpractice.title)
    else:
        await state.update_data(subject=query.data.split(sep="-", maxsplit=1)[1])
        await query.message.answer('Enter the title', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
        await state.set_state(FMSpractice.title)

@router.callback_query(and_f(IsAdmin(), F.data.startswith('add')))
async def add_subject(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'add_subject':
        await query.message.answer('Enter the title', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
        await state.set_state(FMSsubjects.title)
    if query.data == 'add_material':
        response = await supabase.get_subjects()
        subjects = response.data
        text = []
        callback = []
        for subject in subjects:
            text.append(subject['title'])
            callback.append('add_material-'+subject['slug'])
        text.append('« Menu')
        callback.append('add')
        pattern = {
            "caption": (
                "<b>Choose subject</b>\n"
            ),
            "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
        }
        await query.message.edit_caption(**pattern)
        await query.answer()
        await state.set_state(FMSmaterials.subject)
    if query.data == 'add_mock':
        response = await supabase.get_subjects()
        subjects = response.data
        text = []
        callback = []
        for subject in subjects:
            text.append(subject['title'])
            callback.append('add_mock-'+subject['slug'])
        text.append('« Menu')
        callback.append('add')
        pattern = {
            "caption": (
                "<b>Choose subject</b>\n"
            ),
            "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
        }
        await query.message.edit_caption(**pattern)
        await query.answer()
        await state.set_state(FMSmocks.subject)
    if query.data == 'add_practice':
        response = await supabase.get_subjects()
        subjects = response.data
        text = []
        callback = []
        for subject in subjects:
            text.append(subject['title'])
            callback.append('add_practice-'+subject['slug'])
        text.append('« Menu')
        callback.append('add')
        pattern = {
            "caption": (
                "<b>Choose subject</b>\n"
            ),
            "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
        }
        await query.message.edit_caption(**pattern)
        await query.answer()
        await state.set_state(FMSpractice.subject)

@router.message(and_f(IsAdmin(), F.content_type == 'document', FMSmocks.file))
async def add_mock_file(message: types.Message, state: FSMContext):
    await state.update_data(file=message.document.file_id)
    # await supabase.add_material_file(message.photo[0], message.photo[0].file_unique_id)
    await message.answer('Enter the title', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSmocks.title)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSmocks.title))
async def add_mock_title(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(title=message.text)
    await supabase.add_mock(state)
    await state.clear()
    await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Mock has been added successfully', reply_markup=inline_builder(text='« Menu', callback_data='menu'))

@router.message(and_f(IsAdmin(), F.content_type == 'photo', FMSmaterials.file))
async def add_material_photo(message: types.Message, state: FSMContext):
    await state.update_data(file=message.photo[0].file_id)
    # await supabase.add_material_file(message.photo[0], message.photo[0].file_unique_id)
    await message.answer('Enter the title', reply_markup=inline_builder(text='« Cancel', callback_data='cancel'))
    await state.set_state(FMSmaterials.title)

@router.message(and_f(IsAdmin(), F.content_type == 'text', FMSmaterials.title))
async def add_material_title(message: types.Message, state: FSMContext):
    photo = get_project_root('assets/logo.png')
    await state.update_data(title=message.text)
    await supabase.add_material(state)
    await state.clear()
    await message.answer_photo(photo=types.FSInputFile(path=photo), caption='Material has been added successfully', reply_markup=inline_builder(text='« Menu', callback_data='menu'))

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
        "<b>📚 Subject has been deleted successfully</b>"
    )
    await query.message.edit_caption(caption=caption, reply_markup=inline_builder(text=['« Menu'], callback_data=['delete_subject']))
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_mocks-')))
async def delete_mocks(query: types.CallbackQuery):
    pattern = {}
    response = await supabase.get_mocks(query.data.split(sep='-', maxsplit=1)[1])
    mocks = response.data
    buttons = []
    pattern['caption'] = (
        "<b>❌ Delete mock</b>\n"
        "\n"
        "Choose mock to delete"
    )
    buttons = []
    for mock in mocks:
        buttons.append({'text':mock['title'], 'callback_data':'delete_mock-'+str(mock['id'])})
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

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_mock-')))
async def delete_mock(query: types.CallbackQuery):
    await supabase.delete_mock(query.data.split(sep='-', maxsplit=1)[1])
    caption = (
        "<b>📄 Mock has been deleted successfully</b>"
    )
    await query.message.edit_caption(caption=caption, reply_markup=inline_builder(text=['« Menu'], callback_data=['delete_mock']))

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_practices-')))
async def delete_practices(query: types.CallbackQuery):
    pattern = {}
    # slugs = await supabase.get_practice_slug()
    res1 = await supabase.get_subject(query.data.split(sep='-', maxsplit=1)[1])
    subject =res1.data[0]
    slugs = await supabase.get_practices(query.data.split(sep='-', maxsplit=1)[1])
    buttons = []
    pattern['caption'] = (
        "<b>❌ Delete practice</b>\n"
        "\n"
        "Choose practice to delete"
    )
    buttons = []
    for slug in slugs:
        practice = await supabase.get_practice(slug['slug'])
        buttons.append({'text':practice['title']+' - '+subject['title'], 'callback_data':'delete_practice-'+str(practice['slug'])})
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

# @router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_practices')))
# async def delete_practices_subject(query: types.CallbackQuery):
#     response = await supabase.get_subjects()
#     subjects = response.data
#     text = []
#     callback = []
#     for subject in subjects:
#         text.append(subject['title'])
#         callback.append('delete_practices-'+subject['slug'])
#     text.append('« Menu')
#     callback.append('delete_')
#     pattern = {
#         "caption": (
#             "<b>❌ Delete practice</b>\n"
#             "\n"
#             "Choose subject to delete practice from"
#         ),
#         "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
#     }
#     await query.message.edit_caption(**pattern)
#     await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_practice-')))
async def delete_practice(query: types.CallbackQuery):
    await supabase.delete_practice(query.data.split(sep='-', maxsplit=1)[1])
    caption = (
        "<b>⚡️ Practice has been deleted successfully</b>"
    )
    await query.message.edit_caption(caption=caption, reply_markup=inline_builder(text=['« Menu'], callback_data=['delete_practice']))
    await query.answer()

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_materials-')))
async def delete_materials(query: types.CallbackQuery):
    pattern = {}
    response = await supabase.get_materials(query.data.split(sep='-', maxsplit=1)[1])
    materials = response.data
    buttons = []
    pattern['caption'] = (
        "<b>❌ Delete material</b>\n"
        "\n"
        "Choose material to delete"
    )
    buttons = []
    for material in materials:
        buttons.append({'text':material['title'], 'callback_data':'delete_material-'+str(material['id'])})
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

@router.callback_query(and_f(IsAdmin(), F.data.startswith('delete_material-')))
async def delete_material(query: types.CallbackQuery):
    await supabase.delete_material(query.data.split(sep='-', maxsplit=1)[1])
    caption = (
        "<b>📖 Material has been deleted successfully</b>"
    )
    await query.message.edit_caption(caption=caption, reply_markup=inline_builder(text=['« Menu'], callback_data=['delete_material']))
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
    if query.data == 'delete_material':
        response = await supabase.get_subjects()
        subjects = response.data
        buttons = []
        pattern['caption'] = (
            "<b>❌ Delete material</b>\n"
            "\n"
            "Choose subject to delete materials from"
        )
        buttons = []
        for subject in subjects:
            buttons.append({'text':subject['title'], 'callback_data':'delete_materials-'+str(subject['slug'])})
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
    if query.data == 'delete_mock':
        response = await supabase.get_subjects()
        subjects = response.data
        buttons = []
        pattern['caption'] = (
            "<b>❌ Delete mock</b>\n"
            "\n"
            "Choose subject to delete mocks from"
        )
        buttons = []
        for subject in subjects:
            buttons.append({'text':subject['title'], 'callback_data':'delete_mocks-'+str(subject['slug'])})
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
    if query.data == 'delete_practice':
        response = await supabase.get_subjects()
        subjects = response.data
        buttons = []
        pattern['caption'] = (
            "<b>❌ Delete practice</b>\n"
            "\n"
            "Choose subject to delete practice from"
        )
        buttons = []
        for subject in subjects:
            buttons.append({'text':subject['title'], 'callback_data':'delete_practices-'+str(subject['slug'])})
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