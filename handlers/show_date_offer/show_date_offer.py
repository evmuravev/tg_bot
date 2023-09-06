from telegram import (
    Update,
    error,
    File,
)
from telegram.ext import (
    ContextTypes,
)

from db.tasks import get_repository
from db.repositories.date_offers import DateOffersRepository
from handlers.common.users import get_user
from handlers.show_profile.show_profile import get_profile_description
from models.date_offer import DateOfferPublic
from models.user import UserPublic
from utils.utils import escape_markdownv2


DESCRIPTION = """
*Куда хочу на свидание:*
_{where}_
*Когда:*
_{when}_
*С кем хотел бы пойти:*
_{expectations}_
*Если возникнут расходы, то:*
_{bill_splitting}_
"""

BILL_MAP = {
    "on_me": "💸 Я угощаю",
    "split": "🤝 50/50",
    "on_you": "😇 За твой счет"
}


async def get_date_offer_description(date_offer: DateOfferPublic):
    date_offer = date_offer
    date_offer.where = escape_markdownv2(date_offer.where)
    date_offer.when = escape_markdownv2(date_offer.when)
    date_offer.expectations = escape_markdownv2(date_offer.expectations)
    date_offer.bill_splitting = escape_markdownv2(f'{BILL_MAP[date_offer.bill_splitting]}')

    return DESCRIPTION.format(**date_offer.dict())


async def show_date_offer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        dry_run=False
) -> tuple[File, str, DateOfferPublic]:
    user: UserPublic = await get_user(update, context)
    if not user or not user.profile:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Вы еще не создали профиль!',
        )
    date_offer_repo = get_repository(DateOffersRepository, context)
    date_offer: DateOfferPublic = await date_offer_repo.get_date_offer_by_profile_id(
        profile_id=user.profile.id
    )
    profile = await get_profile_description(user.profile)
    date_offfer_description = await get_date_offer_description(date_offer)
    caption = profile.caption + date_offfer_description

    try:
        image = await context.bot.get_file(profile.image)
    except error.BadRequest:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Не могу найти ваше фото... Обновите, пожалйста, профиль или обратитесь к администратору',
        )
    else:
        if not dry_run:
            await context.bot.send_photo(
                    chat_id=update.effective_user.id,
                    photo=image.file_id,
                    caption=caption,
                    parse_mode="MarkdownV2",
                )
    return image, caption, date_offer
