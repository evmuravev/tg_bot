import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.repositories.date_offers import DateOffersRepository
from db.tasks import get_repository
from handlers.date_offer.common import (
    STEPS,
    get_next_step
)
from handlers.common.users import get_user
from models.date_offer import DateOfferUpdate
from models.user import UserPublic


logger = logging.getLogger()

where_text = '''
*Куда вы хотите пойти на свидание?*
_\(например: в кино, на концерт группы DABRO, в кафе и пр\.\)_
'''


async def set_where_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['WHERE']
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=where_text,
        parse_mode="MarkdownV2",
    )
    return step


async def set_where(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    where = update.message.text
    if len(where) <= 300:
        date_offer_repo = get_repository(DateOffersRepository, context)
        date_offer_update = {
            'where': where,
        }
        await date_offer_repo.update_date_offer(
            date_offer_update=DateOfferUpdate(**date_offer_update),
            profile_id=user.profile.id
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Сократите ваш текст до 300 символов\.\.\. Сейчас в нем {len(where)}",
            parse_mode="MarkdownV2",
        )
        return await set_where_step(update, context)

    next_step = get_next_step(STEPS['WHERE'])

    return await next_step(update, context)
