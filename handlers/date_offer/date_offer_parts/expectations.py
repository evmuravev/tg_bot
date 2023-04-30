import logging
from telegram import Update
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

excpectations_text = '''
*Напишите, с кем хотели бы сходить на свидание?*
_\(например: с девушкой, которая любит рок, с паренем с хорошим чувством юмора и тп\.\)_
'''


async def set_excpectations_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['EXPECTATIONS']
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=excpectations_text,
        parse_mode="MarkdownV2",
    )
    return step


async def set_expectations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    expectations = update.message.text
    if len(expectations) <= 1000:
        date_offer_repo: DateOffersRepository = get_repository(DateOffersRepository, context)
        date_offer_update = {
            'expectations': expectations,
        }
        await date_offer_repo.update_date_offer(
            date_offer_update=DateOfferUpdate(**date_offer_update),
            profile_id=user.profile.id
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Сократите ваш текст до 1000 символов\.\.\. Сейчас в нем {len(expectations)}",
            parse_mode="MarkdownV2",
        )
        return await set_excpectations_step(update, context)

    next_step = get_next_step(STEPS['EXPECTATIONS'])

    return await next_step(update, context)


async def excpectations_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(STEPS['EXPECTATIONS'])
    return await previous_step(update, context)
