import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest
from core.config import DATE_TOPIC_ID, TELEGRAM_GROUP_ID
from db.repositories.date_offers import DateOffersRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.menu import menu
from handlers.show_date_offer import show_date_offer_handler, show_date_offer
from handlers.date_offer.common import (
    STEPS
)
from handlers.date_offer.date_offer_parts.where import set_where_step
from models.date_offer import DateOfferUpdate, DateOfferBase, DateOfferPublic
from models.user import UserPublic


logger = logging.getLogger()


async def set_final_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['FINAL_STEP']
):
    await show_date_offer_handler(update, context)

    options = [
        [
            InlineKeyboardButton("🔃 Заново", callback_data='do_start_over'),
            InlineKeyboardButton("Далее ⏩", callback_data='do_final_step'),
        ]
    ]

    keyboard = [*options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Все почти готово\! Так выглядит ваше приглашение на свидание\. Продолжить\?*",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )

    return step


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user: UserPublic = await get_user(update, context)
    date_offer_repo = get_repository(DateOffersRepository, context)

    await date_offer_repo.update_date_offer(
        date_offer_update=DateOfferBase(),
        profile_id=user.profile.id,
        exclude_unset=False
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Заполненное свидание успешно очищено, начинаем сначала :)',
    )
    return await set_where_step(update, context)


async def final_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    date_offer_repo: DateOffersRepository = get_repository(DateOffersRepository, context)
    image, caption, _ = await show_date_offer(user, context)
    options = [
        [
            InlineKeyboardButton("✨ Откликнуться!", callback_data=f'lets_go:{str(user.id)}'),
            InlineKeyboardButton("Пожаловаться 😒", callback_data=f'date_complain:{str(user.profile.id)}'),
        ]
    ]
    keyboard = [*options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    prev_date_offer = await date_offer_repo.get_last_date_offer_by_profile_id(
        profile_id=user.profile.id,
        populate=False
    )
    # check if message from the user already exists
    if prev_date_offer:
        # delete the previous message
        try:
            await context.bot.delete_message(
                chat_id=TELEGRAM_GROUP_ID,
                message_id=prev_date_offer.message_id
            )
        except BadRequest as ex:
            logger.warning(ex)

    message = await context.bot.send_photo(
        chat_id=TELEGRAM_GROUP_ID,
        photo=image.file_id,
        caption=caption,
        parse_mode="MarkdownV2",
        reply_to_message_id=DATE_TOPIC_ID,
        reply_markup=reply_markup
    )

    date_offer_update = {
        'message_id': message.message_id
    }
    await date_offer_repo.update_date_offer(
        date_offer_update=DateOfferUpdate(**date_offer_update),
        profile_id=user.profile.id
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Свидание опубликовано! 💞',
    )
    await menu.menu(update, context)

    return ConversationHandler.END
