import logging
from telegram import Update
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


async def set_bio_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['BIO']
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Напишите о себе*\n_\(увлечения, интересы, хобби и пр\.\ Смело расставляйте \#тэги, чтобы выделиться\! Постарайтесь уложиться в 1000 символов\)_    ↪/back",
        parse_mode="MarkdownV2",
    )

    return step


async def set_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    bio = update.message.text
    if len(bio) <= 1000:
        profile_repo = get_repository(ProfilesRepository, context)
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
