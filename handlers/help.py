# handlers/help.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command

from texts.help import (
    help_main,
    faq_categories,
    faq_category_general_questions,
    faq_category_general_answers,
    instructions_cards,
    instruction_end,
    feedback_choose_type,
    feedback_prompts,
    feedback_thanks,
    feedback_cancelled,
)
from keyboards.help import (
    help_kb,
    faq_categories_kb,
    faq_questions_kb,
    faq_answers_kb,
    instruction_main_kb,
    instruction_kb,
    feedback_type_kb,
    feedback_cancel_kb,
)
from config import ADMINS

router = Router()

async def _safe_edit(cb: CallbackQuery, text: str, markup):
    try:
        await cb.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    except TelegramBadRequest:
        await cb.answer()
    else:
        await cb.answer()

# 1. /help и кнопка «🆘 Помощь»
@router.message(F.text == "🆘 Помощь")
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(help_main, reply_markup=help_kb(), parse_mode="Markdown")

# 2. FAQ: категории
@router.callback_query(F.data == "help:faq")
async def _faq_categories(cb: CallbackQuery):
    await _safe_edit(cb, faq_categories, faq_categories_kb())

# 3. FAQ: вопросы
@router.callback_query(F.data.startswith("faq:category:"))
async def _faq_questions(cb: CallbackQuery):
    _, _, category = cb.data.split(":", 2)
    qs = faq_category_general_questions.get(category, [])
    text = "\n".join(f"• {q}" for q in qs)
    await _safe_edit(cb, text, faq_questions_kb(category))

# 4. FAQ: ответ
@router.callback_query(F.data.startswith("faq:question:"))
async def _faq_answer(cb: CallbackQuery):
    _, _, category, idx = cb.data.split(":")
    idx = int(idx)
    question = faq_category_general_questions.get(category, [])[idx]
    answer = faq_category_general_answers.get(category, {}).get(question, "Ответ не найден.")
    await _safe_edit(cb, answer, faq_answers_kb(category))

# 5. Инструкции: главное меню
@router.callback_query(F.data == "help:instr")
async def _instr_main(cb: CallbackQuery):
    await _safe_edit(cb, "*Инструкции*\n\nВыберите тему:", instruction_main_kb())

# 6. Инструкции: универсальный слайдер
@router.callback_query(F.data.startswith("instr:"))
async def _instr_slide(cb: CallbackQuery):
    parts = cb.data.split(":")
    if len(parts) != 3:
        return await _safe_edit(cb, help_main, help_kb())

    _, topic, idx_str = parts
    try:
        idx = int(idx_str)
    except ValueError:
        return await _safe_edit(cb, help_main, help_kb())

    # выбираем карточки
    if topic in ("create", "join"):
        cards = instructions_cards
    elif topic == "view":
        cards = ["📋 *Где мои поездки?*\nНажмите «🧳 Мои поездки» — здесь вы увидите свои объявления."]
    elif topic == "search":
        cards = ["🔍 *Как искать поездки?*\nНажмите «🔎 Поиск», задайте фильтр и просмотрите результаты."]
    else:
        return await _safe_edit(cb, help_main, help_kb())

    # выход за границы
    if idx < 0 or idx >= len(cards):
        return await _safe_edit(cb, instruction_end, help_kb())

    # показываем последний слайд как окончание
    if idx == len(cards) - 1:
        return await _safe_edit(cb, instruction_end, help_kb())

    slide = cards[idx]
    kb    = instruction_kb(topic, idx, len(cards))
    await _safe_edit(cb, slide, kb)

# 7. Обратная связь: начало
@router.callback_query(F.data == "help:feedback")
async def _fb_start(cb: CallbackQuery):
    await _safe_edit(cb, feedback_choose_type, feedback_type_kb())

# 8. Обратная связь: выбор типа
@router.callback_query(F.data.startswith("fb:type:"))
async def _fb_type(cb: CallbackQuery):
    _, _, ftype = cb.data.split(":")
    prompt = feedback_prompts.get(ftype)
    if not prompt:
        return await cb.answer()
    await cb.message.edit_reply_markup(reply_markup=feedback_cancel_kb())
    await cb.message.answer(prompt, parse_mode="Markdown")

# 9. Обратная связь: сбор любого текста
@router.message()
async def _fb_collect(message: Message):
    text_to_admins = f"🆘 [{message.text[:50]}] @{message.from_user.username}: {message.text}"
    for admin in ADMINS:
        try:
            await message.bot.send_message(admin, text_to_admins)
        except TelegramBadRequest:
            pass
    await message.answer(feedback_thanks, reply_markup=help_kb(), parse_mode="Markdown")

# 10. Кнопка «Домой»
@router.callback_query(F.data == "help:menu")
async def _back_to_help(cb: CallbackQuery):
    await _safe_edit(cb, help_main, help_kb())


# кнопка "Отмена"
@router.callback_query(F.data == "fb:cancel")
async def _fb_cancel(cb: CallbackQuery):
    """
    Обработчик кнопки «Отмена» в форме обратной связи:
    возвращает пользователя в главное меню помощи.
    """
    # analytics:event_logged(help_feedback_cancelled)
    await _safe_edit(cb, help_main, help_kb())
