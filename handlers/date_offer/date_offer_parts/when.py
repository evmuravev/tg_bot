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

when_text = '''
*Когда вы хотите назначить свидание?*
_\(например: завтра, на следующих выходных, 14\.02\.2024 и пр\.\)_
↪/back
'''


async def set_when_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['WHEN']
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=when_text,
        parse_mode="MarkdownV2",
    )
    return step


async def when_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(STEPS['WHEN'])
    return await previous_step(update, context)


async def set_when(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    user: UserPublic = await get_user(update, context)
    when = update.message.text
    if len(when) <= 100:
        date_offer_repo: DateOffersRepository = get_repository(DateOffersRepository, context)
        date_offer_update = {
            'when': when,
        }
        await date_offer_repo.update_date_offer(
            date_offer_update=DateOfferUpdate(**date_offer_update),
            profile_id=user.profile.id
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Сократите ваш текст до 100 символов\.\.\. Сейчас в нем {len(when)}",
            parse_mode="MarkdownV2",
        )
        return await set_when_step(update, context)

    next_step = get_next_step(STEPS['WHEN'])

    return await next_step(update, context)
