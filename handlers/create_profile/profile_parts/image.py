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
from models.profile import ProfileUpdate


logger = logging.getLogger()


async def set_image_step(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_step=STEPS['IMAGE']
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Теперь отправьте свое фото для профиля*\n_\(пожалуйста\, используйте реальное фото\)_    ↪/back",
        parse_mode="MarkdownV2",
    )

    return next_step


async def set_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    file_id = update.message.photo[0].file_id

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Великолепно выглядите\!\n_\(пожауйста, не удаляйте фото из переписки с ботом\)_',
        parse_mode="MarkdownV2",
        read_timeout=60,
        write_timeout=60,
        connect_timeout=60,
        pool_timeout=60,
    )

    profile_repo = get_repository(ProfilesRepository, context)
    profile_update = {
        'image': file_id,
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )
    next_step = get_next_step(STEPS['IMAGE'])
    return await next_step(update, context)


async def image_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(STEPS['IMAGE'])
    return await previous_step(update, context)
