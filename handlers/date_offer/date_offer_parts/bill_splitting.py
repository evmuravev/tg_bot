import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db.repositories.date_offers import DateOffersRepository
from db.tasks import get_repository
from handlers.date_offer.common import (
    STEPS,
    get_next_step,
    get_previous_step
)
from handlers.common.users import get_user
from models.date_offer import DateOfferUpdate
from models.user import UserPublic


logger = logging.getLogger()

async def set_bill_splitting_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['BILL_SPLITTING']
):
    keyboard = [
        [
            InlineKeyboardButton("💸 Я угощаю", callback_data='on_me'),
            InlineKeyboardButton("🤝 50/50", callback_data='split'),
            InlineKeyboardButton("😇 За твой счет", callback_data='on_you')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Как вы хотите разделить расходы?:*    ↪/back",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )

    return step


async def set_bill_splitting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    bill_splitting = update.callback_query.data
    date_offer_repo = get_repository(DateOffersRepository, context)
    date_offer_update = {
        'bill_splitting': bill_splitting
    }
    await date_offer_repo.update_date_offer(
        date_offer_update=DateOfferUpdate(**date_offer_update),
        profile_id=user.profile.id
    )
    next_step = get_next_step(STEPS['BILL_SPLITTING'])
    return await next_step(update, context)


async def bill_splitting_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(STEPS['BILL_SPLITTING'])
    return await previous_step(update, context)
