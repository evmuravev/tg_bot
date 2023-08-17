import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.update_profile.common import (
    STEPS,
    get_next_step
)
from models.profile import ProfileUpdate
from models.user import UserPublic

logger = logging.getLogger()


async def set_sex_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['SEX']
):
    SEX_MAP = {
        "m": "муж",
        "f": "жен"
    }
    user: UserPublic = await get_user(update, context)
    sex = SEX_MAP[user.profile.sex]

    keyboard = [
        [
            InlineKeyboardButton("👨 Мужчина", callback_data='m'),
            InlineKeyboardButton("👩 Женщина", callback_data='f')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"*Ваш пол \- {sex}:*\n_\(укажите исправление или нажмите  ⏩ /skip \)_",
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


async def sex_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(STEPS['SEX'])
    return await next_step(update, context)
