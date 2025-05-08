from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import get_unread_notifications, mark_notification_read

router = Router()


# ✅ Пометка уведомления как прочитанного
@router.callback_query(F.data.startswith("notif_read:"))
async def mark_read(callback: CallbackQuery):
    notif_id = int(callback.data.split(":")[1])
    mark_notification_read(notif_id)
    await callback.message.edit_text("✅ Уведомление прочитано.")
    await callback.answer()


def notification_filter_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📩 Присоединения", callback_data="notif_filter:new_join"),
            InlineKeyboardButton(text="👥 Подписчики", callback_data="notif_filter:new_follower")
        ],
        [
            InlineKeyboardButton(text="🔗 По ссылке", callback_data="notif_filter:joined_by_link"),
            InlineKeyboardButton(text="⚙ Системные", callback_data="notif_filter:system")
        ],
        [
            InlineKeyboardButton(text="✅ Прочитанные", callback_data="notif_filter:read"),
            InlineKeyboardButton(text="🔄 Все", callback_data="notif_filter:all")
        ]
    ])
