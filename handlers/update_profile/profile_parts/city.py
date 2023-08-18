import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
)
from core.references.cities import CITIES
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.update_profile.common import (
    STEPS,
    get_next_step
)
from models.profile import ProfileUpdate
from models.user import UserPublic
from utils.utils import escape_markdownv2


logger = logging.getLogger()

PAGE_SIZE = 5


async def set_city_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['REGION']
):
    region_options = list(CITIES.keys())
    context.user_data["region_options"] = region_options
    context.user_data["region_page"] = 0
    return await send_region_page(update, context)


async def send_region_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    region_options = context.user_data["region_options"]
    region_page = context.user_data["region_page"]
    region_keyboard = [
        [InlineKeyboardButton(region, callback_data=region)]
        for region in region_options[region_page*PAGE_SIZE:(region_page+1)*PAGE_SIZE]
    ]
    navigation = []
    if region_page > 0:
        navigation.append(InlineKeyboardButton("⏪ Назад", callback_data="prev_region"))
    if (region_page+1)*PAGE_SIZE < len(region_options):
        navigation.append(InlineKeyboardButton("Вперед ⏩", callback_data="next_region"))
    region_keyboard.append(navigation)
    region_markup = InlineKeyboardMarkup(region_keyboard)

    user: UserPublic = await get_user(update, context)
    region = user.profile.region
    city = user.profile.city
    full_city = escape_markdownv2(f'{region}, {city}')

    if update.message:
        await update.message.reply_text(
            text=f"*Ваш текущий город \- {full_city}:*\n_\(укажите исправление или нажмите  /skip ⏩   \)_",
            reply_markup=region_markup,
            parse_mode="MarkdownV2"
        )
    else:
        await update.callback_query.edit_message_text(
            text=f"*Ваш текущий город \- {full_city}:*\n_\(укажите исправление или нажмите  /skip ⏩   \)_",
            reply_markup=region_markup,
            parse_mode="MarkdownV2"
        )
    return STEPS['REGION']


async def set_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    region = query.data
    context.user_data["selected_region"] = region
    city_options = CITIES[region]
    context.user_data["city_options"] = city_options
    context.user_data["city_page"] = 0

    await send_city_page(update, context)
    return STEPS['CITY']


async def send_city_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city_options = context.user_data["city_options"]
    city_page = context.user_data["city_page"]
    city_keyboard = [
        [InlineKeyboardButton(city, callback_data=city)]
        for city in city_options[city_page*PAGE_SIZE:(city_page+1)*PAGE_SIZE]
    ]
    navigation = []
    if city_page > 0:
        navigation.append(InlineKeyboardButton("⏪ Назад", callback_data="prev_city"))
    if (city_page+1)*PAGE_SIZE < len(city_options):
        navigation.append(InlineKeyboardButton("Вперед ⏩", callback_data="next_city"))
    city_keyboard.insert(0, [InlineKeyboardButton("К выбору региона ⤴", callback_data="back_to_regions")])
    city_keyboard.append(navigation)
    city_markup = InlineKeyboardMarkup(city_keyboard)
    query = update.callback_query
    region = context.user_data['selected_region'].replace('-', '\-')
    await query.edit_message_text(
        text=f"_Выбранный регион {region}\._\nТеперь выберите город:",
        reply_markup=city_markup,
        parse_mode="MarkdownV2"
    )


async def set_city(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    user = query.from_user
    city = query.data
    region = context.user_data["selected_region"]
    await query.answer()
    await query.edit_message_text(text=f"Ах чудесный город {city}!")

    profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)
    profile_update = {
        'city': city,
        'region': region
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )
    next_step = get_next_step(STEPS['CITY'])
    return await next_step(update, context)


async def region_pagination_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    region_page = context.user_data["region_page"]
    direction = query.data
    if direction == "prev_region":
        region_page -= 1
    elif direction == "next_region":
        region_page += 1
    context.user_data["region_page"] = region_page
    await send_region_page(update, context)


async def city_pagination_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    city_page = context.user_data["city_page"]
    direction = query.data
    if direction == "prev_city":
        city_page -= 1
    elif direction == "next_city":
        city_page += 1
    context.user_data["city_page"] = city_page
    await send_city_page(update, context)


async def back_to_regions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    return await send_region_page(update, context)


async def city_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(STEPS['CITY'])
    return await next_step(update, context)
