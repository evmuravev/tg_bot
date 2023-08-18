from dataclasses import dataclass
from telegram import (
    Update,
    error
)
from telegram.ext import (
    ContextTypes,
)

from handlers.common.users import get_user
from models.profile import ProfilePublic
from models.user import UserPublic
from utils.utils import add_age_postfix, escape_markdownv2


DESCRIPTION = """
*{name}*, *{age}*

*О себе:*
_{bio}_

{city} {age_tag} {sex}
"""

SEX_MAP = {
    "m": "муж",
    "f": "жен"
}


@dataclass
class Profile:
    image: str
    caption: str


async def get_profile_description(user_profile: ProfilePublic):
    profile = user_profile
    profile.name = escape_markdownv2(profile.name)
    profile.bio = escape_markdownv2(profile.bio)
    if profile.city != profile.region:
        profile.city = escape_markdownv2(
            f"#{profile.city.replace('-','_').replace(' ','_')} #{profile.region.replace('-','_').replace(' ','_')}"
        )
    else:
        profile.city = escape_markdownv2(f"#{profile.city.replace('-','_').replace(' ','_')}")
    profile.age_tag = escape_markdownv2(profile.age_tag)
    profile.sex = escape_markdownv2(f'#{SEX_MAP[profile.sex]}')
    profile.age = add_age_postfix(profile.age)

    return Profile(user_profile.image, DESCRIPTION.format(**profile.dict()))


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, dry_run=False):
    user: UserPublic = await get_user(update, context)
    if not user or not user.profile:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Вы еще не создали профиль!',
        )

    profile = await get_profile_description(user.profile)

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
                    caption=profile.caption,
                    parse_mode="MarkdownV2",
                )
    return image, profile.caption

    # TODO Если фото нет и статус new - вернуть к первому шагу
    # TODO если partially - вернуть к шагу с фото
    # TODO если approved - показать и предложить кнопку обновления
