import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler
)
from core.config import TELEGRAM_GROUP_ID
from db.repositories.date_offers import DateOffersRepository
from db.repositories.profiles import ProfilesRepository

from db.tasks import get_repository
from handlers.common.users import get_user
from models.date_offer import DateOfferPublic
from models.profile import ProfileStatus, ProfileUpdate
from models.user import UserPublic


logger = logging.getLogger()


STEPS = {
    'DELETE': 0,
}


async def delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("❌ Удалить", callback_data='confirm_deletion'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Вы действительно хотите удалить все данные о себе?* Для отмены нажмите\: ↪/cancel\_deletion",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )

    return STEPS['DELETE']


async def confirm_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)
    profile_update = {
        'status': ProfileStatus.deleted
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )
    # check if message from the user already exists
    date_offer_repo: DateOffersRepository = get_repository(DateOffersRepository, context)
    date_offer: DateOfferPublic = await date_offer_repo.get_previous_date_offer_by_profile_id(
        profile_id=user.profile.id
    )
    if date_offer and date_offer.message_id is not None:
        # delete the previous message
        try:
            await context.bot.delete_message(
                chat_id=TELEGRAM_GROUP_ID,
                message_id=date_offer.message_id
            )
        except BadRequest as ex:
            logger.warning(ex)

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Ваш профиль и свидания были удалены, нам очень жаль\.\.\.",
        parse_mode="MarkdownV2",
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Пользователь %s отменил удаление.", user.first_name)
    await update.message.reply_text(
        'Рады, что вы с нами!'
    )

    return ConversationHandler.END


DELETE_PROFILE_CONVERSATION = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CommandHandler('delete_profile', delete_profile),
        CallbackQueryHandler(delete_profile, pattern='delete_profile')],
    states={
        STEPS['DELETE']: [
            CallbackQueryHandler(confirm_deletion, pattern='^confirm_deletion$')
        ]
    },

    fallbacks=[CommandHandler('cancel_deletion', cancel)],
)
