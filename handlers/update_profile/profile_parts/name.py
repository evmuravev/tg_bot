import logging
from telegram import Update
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
from utils.utils import escape_markdownv2


logger = logging.getLogger()


async def set_name_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['NAME']
):
    user: UserPublic = await get_user(update, context)
    name = escape_markdownv2(user.profile.name)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f'*Ваше текущее имя \- {name}*\n_\(напишите новое имя или нажмите  /skip ⏩   \)_',
        parse_mode="MarkdownV2",
    )
    return step


async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = update.message.text
    profile_repo = get_repository(ProfilesRepository, context)
    profile_update = {
        'name': name
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )

    next_step = get_next_step(STEPS['NAME'])
    return await next_step(update, context)


async def name_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(STEPS['NAME'])
    return await next_step(update, context)
