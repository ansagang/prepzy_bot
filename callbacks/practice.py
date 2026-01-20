from aiogram import Router, F
from aiogram import types

from database import supabase

from keyboards import inline_builder
from keyboards import keyboard

from utils import KeyboardPaginator, get_project_root

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.filters import or_f
from json import loads, dumps
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

router = Router()

def compose_markup(question: int, slug):
    cd1 = {
        "q": question,
        "a": 1,
        "slug": slug
    }
    cd2 = {
        "q": question,
        "a": 2,
        "slug": slug
    }
    cd3 = {
        "q": question,
        "a": 3,
        "slug": slug
    }
    cd4 = {
        "q": question,
        "a": 4,
        "slug": slug
    }
    km = inline_builder(text=['A', 'B', 'C', 'D', 'Stop practice', "« Menu"], callback_data=[dumps(cd1), dumps(cd2), dumps(cd3), dumps(cd4), 'stop_'+slug, 'cancel-practice_'+slug], sizes=[4, 1, 1])
    
    return km

async def reset(id_: int, practice):
    await supabase.set_in_process(id_, False, practice)
    await supabase.update_questions_passed(id_, 0, practice)
    await supabase.update_questions_message(id_, 0, practice)
    await supabase.update_current_question(id_, 0, practice)

@router.callback_query(F.data.startswith("cancel-practice_"))
async def cancel_practice(query: types.CallbackQuery):
    slug = query.data.split(sep="_", maxsplit=1)[1]
    await supabase.set_in_process(query.from_user.id, False, slug)
    await query.message.delete()

@router.callback_query(F.data.startswith('practice_'))
async def go_handler(query: types.CallbackQuery):
    slug = query.data.split(sep="_", maxsplit=1)[1]
    practice = await supabase.get_practices_full(slug)
    if not await supabase.exists(query.from_user.id, slug):
        await supabase.add_score(query.from_user.id, slug)
    if await supabase.is_in_process(query.from_user.id, slug):
        msg = await query.bot.send_message(query.from_user.id, "🚫 You cannot start the same practice until you finish this one.")
        time.sleep(3)
        await query.bot.delete_message(query.from_user.id, msg.message_id)
        return
    await supabase.set_in_process(query.from_user.id, True, slug)
    msg = await query.bot.send_photo(
        chat_id=query.from_user.id,
        photo=practice[0]['filename'],
        caption=f"{practice[0]['question']}",
        reply_markup=compose_markup(0, slug),
        parse_mode="MarkdownV2"
    )
    await supabase.update_questions_message(query.from_user.id, msg.message_id, slug)
    await supabase.update_current_question(query.from_user.id, 0, slug)
    await supabase.update_questions_passed(query.from_user.id, 0, slug)

async def quit(query):
    slug = query.data.split(sep="_", maxsplit=1)[1]
    passed = await supabase.get_questions_passed(query.from_user.id, slug)
    practice = await supabase.get_practices_full(slug)
    if not await supabase.is_in_process(query.from_user.id, slug):
        return
    user = query.from_user.username
    result = str(passed['questions_passed']) + "/" + str(len(practice))
    await supabase.change_score(query.from_user.id, slug, result, user)
    await supabase.set_in_process(query.from_user.id, False, slug)

@router.callback_query(F.data.startswith('stop_'))
async def quit_handler(query: types.CallbackQuery):
    slug = query.data.split(sep="_", maxsplit=1)[1]
    passed = await supabase.get_questions_passed(query.from_user.id, slug)
    practice = await supabase.get_practices_full(slug)
    user = query.from_user.username
    result = str(passed['questions_passed']) + "/" + str(len(practice))
    await supabase.change_score(query.from_user.id, slug, result, user)
    await supabase.set_in_process(query.from_user.id, False, slug)
    photo = get_project_root('assets/logo.png')
    pattern = {
        "caption": (
            "<b>You have successfully finished the practice! 🎉</b>"
            "\n"
            f"Your score: <b>{passed['questions_passed']}/{len(practice)}</b>"
        ),
        "reply_markup": inline_builder(text='« Menu', callback_data='delete', sizes=1),
        "chat_id": query.from_user.id,
        "photo": types.FSInputFile(path=photo),
    }
    await query.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.bot.send_photo(**pattern)
    await quit(query)

@router.callback_query(lambda c: True)
async def tests(query: types.CallbackQuery):
    data = loads(query.data)
    q = data.get('q')
    slug = data.get('slug')
    practice = await supabase.get_practices_full(slug)
    is_correct = int(practice[q]['answer']) == data['a']
    passed = await supabase.get_questions_passed(query.from_user.id, slug)
    msg = await supabase.get_questions_message(query.from_user.id, slug)
    if is_correct:
        passed['questions_passed'] += 1
        await supabase.update_questions_passed(query.from_user.id, passed['questions_passed'], slug)
    if q + 1 > len(practice) - 1:
        user = query.from_user.username
        result = str(passed['questions_passed']) + "/" + str(len(practice))
        await supabase.change_score(query.from_user.id, slug, result, user)
        await supabase.set_in_process(query.from_user.id, False, slug)
        # await reset(query.from_user.id, slug)
        await query.bot.delete_message(query.from_user.id, msg['questions_message'])
        photo = get_project_root('assets/logo.png')
        pattern = {
            "caption": (
                "<b>You have successfully finished the practice! 🎉</b>"
                "\n"
                f"Your score: <b>{passed['questions_passed']}/{len(practice)}</b>"
            ),
            "reply_markup": inline_builder(text='« Menu', callback_data='delete', sizes=1),
            "chat_id": query.from_user.id,
            "photo": types.FSInputFile(path=photo)
        }
        await query.bot.send_photo(**pattern)
        return
    await query.bot.edit_message_media(
        media=types.InputMediaPhoto(media=practice[q + 1]['filename']),
        chat_id=query.from_user.id,
        message_id=msg['questions_message'],
        reply_markup=compose_markup(q + 1, slug),
    )
    await query.bot.edit_message_caption(
        caption=f"{practice[q+1]['question']}",
        chat_id=query.from_user.id,
        message_id=msg['questions_message'],
        reply_markup=compose_markup(q + 1, slug),
        parse_mode="MarkdownV2"
    )