import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.create_profile.common import (
    STEPS,
    get_next_step
)
from models.profile import ProfileStatus, ProfileUpdate


logger = logging.getLogger()


async def set_name_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['NAME']
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='*Напишите Ваше имя*\n_\(пожалуйста, не используйте ники, кличики и т\.п\.\)_',
        parse_mode="MarkdownV2",
    )
    return step


async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = update.message.text
    profile_repo = get_repository(ProfilesRepository, context)
    profile_update = {
        'name': name,
        'status': ProfileStatus.partially_completed
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )

    next_step = get_next_step(STEPS['NAME'])
    return await next_step(update, context)
