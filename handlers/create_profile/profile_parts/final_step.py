import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from core.config import ADMIN_IDS
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.menu import menu
from handlers.show_profile import show_profile
from handlers.create_profile.common import (
    STEPS
)
from handlers.create_profile.profile_parts.name import set_name_step
from models.profile import ProfileBase, ProfileStatus, ProfileUpdate
from models.user import UserPublic


logger = logging.getLogger()


async def set_final_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['FINAL_STEP']
):
    await show_profile(update, context)

    options = [
        [
            InlineKeyboardButton("🔃 Заново", callback_data='start_over'),
            InlineKeyboardButton("Далее ⏩", callback_data='final_step'),
        ]
    ]

    keyboard = [*options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Все почти готово\! Так выглядит ваш профиль\. Завершаем создание профиля\?*",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )

    return step


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.callback_query.from_user
    profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)

    await profile_repo.update_profile(
        profile_update=ProfileBase(),
        user_id=user.id,
        exclude_unset=False
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Заполненный профиль успешно очищен, начинаем сначала :)',
    )
    return await set_name_step(update, context)



async def final_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)
    profile_update = {
        'status': ProfileStatus.completed
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )

    ## Отправка уведомления о новой регистрации админу
    # profile = await show_profile.get_profile_description(user.profile)
    # selected_admin = random.choice(ADMIN_IDS)

    # await context.bot.send_photo(
    #         chat_id=selected_admin,
    #         photo=profile.image,
    #         caption='Новая регистрация:' + profile.caption,
    #         parse_mode="MarkdownV2"
    # )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Теперь вы можете всё!)',
    )
    await menu.menu(update, context)

    return ConversationHandler.END
