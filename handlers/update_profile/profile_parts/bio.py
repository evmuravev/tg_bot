import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.update_profile.common import (
    STEPS,
    get_next_step,
    get_previous_step
)
from models.profile import ProfileStatus, ProfileUpdate
from models.user import UserPublic
from utils.utils import escape_markdownv2


logger = logging.getLogger()


async def set_bio_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['BIO']
):
    user: UserPublic = await get_user(update, context)
    bio = escape_markdownv2(user.profile.bio)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=bio,
        parse_mode="MarkdownV2",
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Ваше опиcание профиля выше:*\n_\(укажите новое или нажмите  /skip ⏩   \)_",
        parse_mode="MarkdownV2",
    )

    return step


async def set_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    bio = update.message.text
    if len(bio) <= 1000:
        profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)
        profile_update = {
            'bio': bio,
            'status': ProfileStatus.completed
        }
        await profile_repo.update_profile(
            profile_update=ProfileUpdate(**profile_update),
            user_id=user.id
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Сократите ваш текст до 1000 символов\.\.\. Сейчас в нем {len(bio)}",
            parse_mode="MarkdownV2",
        )
        return await set_bio_step(update, context)

    next_step = get_next_step(STEPS['BIO'])
    return await next_step(update, context)


async def bio_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(STEPS['BIO'])
    return await previous_step(update, context)


async def bio_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(STEPS['BIO'])
    return await next_step(update, context)
