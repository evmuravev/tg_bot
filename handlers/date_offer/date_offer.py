import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)

from db.tasks import get_repository
from db.repositories.date_offers import DateOffersRepository
from models.user import UserPublic
from models.date_offer import DateOfferCreate
from handlers.date_offer.date_offer_parts import (
    expectations, where, when, bill_splitting, cancel, final_step
)
from handlers.date_offer.common import STEPS
from handlers.common.users import get_user


logger = logging.getLogger()


async def date_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    if not user or not user.profile:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Вы еще не создали профиль!',
        )
    date_offer_repo: DateOffersRepository = get_repository(DateOffersRepository, context)
    date_offer_create = DateOfferCreate(profile_id=user.profile.id)
    await date_offer_repo.create_date_offer_for_profile(
        date_offer_create=date_offer_create
    )
    return await where.set_where_step(update, context)


DATE_OFFER_CONVERSATION = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CommandHandler('date_offer', date_offer),
        CallbackQueryHandler(date_offer, pattern='date_offer')],

    states={
        STEPS['WHERE']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, where.set_where),
        ],
        STEPS['WHEN']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, when.set_when),
            CommandHandler('back', when.when_back)
        ],
        STEPS['EXPECTATIONS']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, expectations.set_expectations),
            CommandHandler('back', expectations.excpectations_back),
        ],
        STEPS['BILL_SPLITTING']: [
            CallbackQueryHandler(bill_splitting.set_bill_splitting),
            CommandHandler('back', bill_splitting.bill_splitting_back),
        ],
        STEPS['FINAL_STEP']: [
            CallbackQueryHandler(final_step.start_over, pattern='do_start_over'),
            CallbackQueryHandler(final_step.final_step, pattern='do_final_step'),
        ],
    },

    fallbacks=[CommandHandler('cancel', cancel.cancel)],
)
