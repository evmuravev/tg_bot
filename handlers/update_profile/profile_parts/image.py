import logging
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.update_profile.common import (
    STEPS,
    get_next_step,
)
from models.profile import ProfileUpdate
from models.user import UserPublic


logger = logging.getLogger()


async def set_image_step(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_step=STEPS['IMAGE']
):
    user: UserPublic = await get_user(update, context)
    try:
        await context.bot.send_photo(
                chat_id=update.effective_user.id,
                photo=user.profile.image,
                parse_mode="MarkdownV2",
        )
    except BadRequest as ex:
        logger.warning(ex)
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Фото отсутствует, приложите новое фото",
            parse_mode="MarkdownV2",
        )
        return next_step

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Ваше текущее фото выше:*\n_\(приложите новое или нажмите  /skip ⏩   \)_",
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


async def image_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(STEPS['IMAGE'])
    return await next_step(update, context)
