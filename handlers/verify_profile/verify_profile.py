from telegram import Update
from telegram.ext import ContextTypes

from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from models.profile import ProfileStatus, ProfileUpdate


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status, user = update.callback_query.data.split(':')
    statuses = {
        'approve': ProfileStatus.approved,
        'reject': ProfileStatus.rejected
    }

    profile_repo = get_repository(ProfilesRepository, context)
    profile_update = {
        'status': statuses[status]
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=int(user)
    )
    match status:
        case 'approve':
            text = '🙌Поздравляем! Ваш профиль прошел модерацию! \
\nТеперь вы можете приглашать и откликаться на свидания! /menu'
        case 'reject':
            text = '😞 К сожалению, профиль отклонила администрация! \
\nНичего страшного, просто создайте другой, следуя правилам /create_profile'

    await context.bot.send_message(
        chat_id=int(user),
        text=text,
    )
