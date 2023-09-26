import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from core.config import NEW_PROFILE_TOPIC_ID, TELEGRAM_ADMIN_GROUP_ID
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.menu import menu
from handlers.show_profile import show_profile_handler, show_profile
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
    await show_profile_handler(update, context)

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
    profile_repo = get_repository(ProfilesRepository, context)

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
    profile_repo = get_repository(ProfilesRepository, context)
    profile_update = {
        'status': ProfileStatus.completed
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )

    # # Отправка уведомления о новой регистрации админу
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Перенести в жалобы 😒", callback_data=f'profile_complain:{str(user.profile.id)}')]]
    )
    image, caption = await show_profile(user, context)
    await context.bot.send_photo(
            chat_id=TELEGRAM_ADMIN_GROUP_ID,
            photo=image.file_id,
            caption='Новая регистрация:' + caption,
            parse_mode="MarkdownV2",
            reply_to_message_id=NEW_PROFILE_TOPIC_ID,
            reply_markup=reply_markup
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Теперь вы можете всё! 💪',
    )
    await menu.menu(update, context)

    return ConversationHandler.END
