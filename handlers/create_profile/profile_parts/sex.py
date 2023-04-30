import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.create_profile.common import (
    STEPS,
    get_next_step,
    get_previous_step
)
from models.profile import ProfileStatus, ProfileUpdate

logger = logging.getLogger()


async def set_sex_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['SEX']
):
    keyboard = [
        [
            InlineKeyboardButton("👨 Мужчина", callback_data='m'),
            InlineKeyboardButton("👩 Женщина", callback_data='f')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Укажите ваш пол:*    ↪/back",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )

    return step


async def set_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.callback_query.from_user
    sex = update.callback_query.data
    profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)
    profile_update = {
        'sex': sex
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )
    next_step = get_next_step(STEPS['SEX'])
    return await next_step(update, context)


async def sex_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(STEPS['SEX'])
    return await previous_step(update, context)
