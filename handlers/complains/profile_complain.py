from dataclasses import dataclass
from telegram import (
    Update,
    error
)
from telegram.ext import (
    ContextTypes,
)

from handlers.common.users import get_user
from models.profile import ProfilePublic
from models.user import UserPublic



async def profile_complain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)

    if not user or not user.profile:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Вы еще не создали профиль!\nПерейдите в бот для создания',
        )
    if user.is_banned:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Вы были забанены и больше не можете совершать действия!',
        )
    else:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Ваша жалоба отправлена!',
        )
