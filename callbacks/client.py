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
            "<b>Bot information</b>\n"
            "• Use command /info or just write Info in the chat\n"
            "\n"
            "<b>How to start practice test ❓</b>\n"
            "• Use command /practice\n"
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

# @router.callback_query(F.data == "leaderboard")
# async def materials(query: types.CallbackQuery):
#     ids = await sqlite.sql_get_testing_id()
#     buttons = []
#     for id in ids:
#         buttons.append({'text':id[0], 'callback_data': 'leaderboard_'+id[0]})
#     additional_buttons = [
#         [
#             types.InlineKeyboardButton(text='« Назад', callback_data="menu"),
#         ],
#     ]
#     paginator = KeyboardPaginator(
#         data=buttons,
#         router=router,
#         per_page=5,
#         per_row=1,
#         additional_buttons=additional_buttons
#     )
#     pattern = {
#         "caption": (
#             "<b>Таблица лидеров</b>\n"
#             "\n"
#             "-Выберите тестирование"
#         ),
#         "reply_markup": paginator.as_markup()
#     }
#     await query.message.edit_caption(**pattern)
#     await query.answer()

# @router.callback_query(F.data.startswith('leaderboard_'))
# async def materials(query: types.CallbackQuery):
#     testing_id = query.data.split(sep="_", maxsplit=1)[1]
#     leaderboard = sqlite.get_leaderboard(testing_id)
#     def place():
#         for i in range(len(leaderboard)):
#             if leaderboard[i][0] == query.from_user.id:
#                 return i+1
#     user_place = place()
#     print(leaderboard)
#     places = {"first": "", "second": "", "third": "", "user_place": ""}
#     if 0 < len(leaderboard):
#         places["first"] = f"1 место - @{leaderboard[0][7]} ({leaderboard[0][6]})"
#     else:
#         places["first"] = f"1 место - Нету"

#     if 1 < len(leaderboard):
#         places["second"] = f"2 место - @{leaderboard[1][7]} ({leaderboard[1][6]})"
#     else:
#         places["second"] = f"2 место - Нету"

#     if 2 < len(leaderboard):
#         places["third"] = f"3 место - @{leaderboard[2][7]} ({leaderboard[2][6]})"
#     else:
#         places["third"] = f"3 место - Нету"
#     if user_place:
#         places['user_place'] = f"Вы на {user_place} месте ({leaderboard[user_place-1][6]})"
#     pattern = {
#         "caption": (
#             "<b>Таблица лидеров: </b>\n"
#             "\n"
#             f"{places['first']} 🥇\n"
#             f"{places['second']} 🥈\n"
#             f"{places['third']} 🥉\n"
#             "\n"
#             f"{places['user_place']}"
#         ),
#         "reply_markup": inline_builder(text='« Назад', callback_data="leaderboard")
#     }
#     await query.message.edit_caption(**pattern)
#     await query.answer()

# @router.callback_query(F.data == "testing")
# async def materials(query: types.CallbackQuery):
#     ids = await sqlite.sql_get_testing_id()
#     users = sqlite.get_user(query.from_user.id)
#     results = []
#     for user in users:
#         results.append({'testing_id': user[5], 'result': user[6]})
#     buttons = []
#     for id in ids:
#         buttons.append({'text':id[0], 'callback_data': 'testing_'+id[0]})
#     additional_buttons = [
#         [
#             types.InlineKeyboardButton(text='« Назад', callback_data="menu"),
#         ],
#     ]
#     paginator = KeyboardPaginator(
#         data=buttons,
#         router=router,
#         per_page=5,
#         per_row=1,
#         additional_buttons=additional_buttons
#     )
#     stoke = ""
#     for result in results:
#         stoke += f"{result['testing_id']}: {result['result']} \n"
#     pattern = {
#         "caption": (
#             "<b>Тестирование</b>\n"
#             "\n"
#             "-Выберите тестирование"
#         ),
#         "reply_markup": paginator.as_markup()
#     }
#     await query.message.edit_caption(**pattern)
#     await query.answer()

# @router.callback_query(F.data == "materials")
# async def materials(query: types.CallbackQuery):
#     subjects = await sqlite.sql_get_materials_subjects()
#     text = []
#     callback = []
#     for subject in subjects:
#         text.append(subject[0])
#         callback.append('materials_'+subject[0])
#     text.append('« Назад')
#     callback.append('menu')
#     pattern = {
#         "caption": (
#             "<b>📚 Материалы</b>\n"
#             "\n"
#             "-Выберите предмет"
#         ),
#         "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
#     }
#     await query.message.edit_caption(**pattern)
#     await query.answer()

@router.callback_query(F.data.startswith('subject_'))
async def subject(query: types.CallbackQuery):
    response = await supabase.get_subject(query.data.split(sep="_", maxsplit=1)[1])
    subject = response.data[0]
    print(response)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="« Menu", callback_data="subjects")
    pattern = {
        "caption": (
            f"<b>{subject['title']}</b>\n"
            "\n"
            f"{subject['description']}"
        ),
        "reply_markup": keyboard.as_markup(),
    }
    await query.message.edit_caption(**pattern)
    await query.answer()

# @router.callback_query(F.data.startswith('material_'))
# async def material(query: types.CallbackQuery):
#     material = await sqlite.sql_get_material(query.data.replace('material_', ''))
#     pattern = {
#         "caption": (
#             "<b>"+material[1]+"</b>\n"
#             "\n"
#             "📚 "+material[2]
#         ),
#         "reply_markup": inline_builder(text='« Назад', callback_data='delete', sizes=1),
#         "photo": material[0]
#     }
#     await query.message.answer_photo(**pattern)
#     await query.answer()

# @router.callback_query(F.data == "tests")
# async def tests(query: types.CallbackQuery):
#     subjects = await sqlite.sql_get_tests_subjects()
#     text = []
#     callback = []
#     for subject in subjects:
#         text.append(subject[0])
#         callback.append('tests_'+subject[0])
#     text.append('« Назад')
#     callback.append('menu')
#     pattern = {
#         "caption": (
#             "<b>📄 Пробники</b>\n"
#             "\n"
#             "-Выберите предмет"
#         ),
#         "reply_markup": inline_builder(text=text, callback_data=callback, sizes=1)
#     }
#     await query.message.edit_caption(**pattern)
#     await query.answer()

# @router.callback_query(F.data.startswith('tests_'))
# async def tests(query: types.CallbackQuery):
#     tests = await sqlite.sql_get_tests(query.data.split(sep="_", maxsplit=1)[1])
#     buttons = []
#     for test in tests:
#         buttons.append({'text':test[3], 'callback_data':'test_'+test[3]})
#     additional_buttons = [
#         [
#             types.InlineKeyboardButton(text='« Назад', callback_data="tests"),
#         ],
#     ]
#     paginator = KeyboardPaginator(
#         data=buttons,
#         router=router,
#         per_page=5,
#         per_row=1,
#         additional_buttons=additional_buttons
#     )
#     pattern = {
#         "caption": (
#             "<b>📄 Пробники</b>\n"
#             "\n"
#         ),
#         "reply_markup": paginator.as_markup()
#     }
#     await query.message.edit_caption(**pattern)
#     await query.answer()

# @router.callback_query(F.data.startswith('test_'))
# async def test(query: types.CallbackQuery):
#     test = await sqlite.sql_get_test(query.data.replace('test_', ''))
#     pattern = {
#         "caption": (
#             "<b>"+test[1]+"</b>\n"
#             "\n"
#             "📄 "+test[2]
#         ),
#         "reply_markup": inline_builder(text='« Назад', callback_data='delete', sizes=1),
#         "document": test[0]
#     }
#     await query.message.answer_document(**pattern)
#     await query.answer()

# @router.callback_query(F.data == "delete")
# async def delete(query: types.CallbackQuery):
#     await query.message.delete()

# @router.callback_query(F.data == "menu")
# async def menu(query: types.CallbackQuery, isAdmin: bool):
    
#     kb = main_kb.inlineKb(isAdmin)
#     await query.message.edit_caption(caption="", reply_markup=kb)
#     await query.answer()

# @router.callback_query(F.data == 'cancel')
# async def cancel(query: types.CallbackQuery, state: FSMContext):
#     photo = get_project_root('assets/logo.png')
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#     await state.clear()
#     await query.message.answer_photo(photo=types.FSInputFile(path=photo), caption='Отмена тестирования', reply_markup=inline_builder(text='« Меню', callback_data='menu'))