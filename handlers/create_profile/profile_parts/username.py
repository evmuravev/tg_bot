import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db.repositories.users import UsersRepository
from db.tasks import get_repository
from handlers.create_profile.common import (
    STEPS
)
import handlers.create_profile.create_profile as cp
from models.user import UserUpdate


logger = logging.getLogger()

TEXT = """
*К сожалению\, у вас не задан @username\.*
Это необходимо для того, что ваш профиль могли найти \:\)
Для продолжения задайте в настройках телеграм username
и нажмите на кнопку:
"""


async def set_username_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['USERNAME']
):
    keyboard = [
        [InlineKeyboardButton("Продолжить 🏄", callback_data='set_username')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=TEXT,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )

    return step


async def set_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username:
        return await set_username_step(update, context)

    user_repo = get_repository(UsersRepository, context)
    await user_repo.update_username(
        user=UserUpdate(**user._get_attrs())
    )

    return await cp.create_profile(update, context)
