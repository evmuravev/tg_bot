from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.common.users import get_user
from models.user import UserPublic
from models.profile import ProfileStatus


async def check_profile_exists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    if user and user.profile and user.profile.status == ProfileStatus.completed:
        return True


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile_created = await check_profile_exists(update, context)
    if profile_created:
        profile = [
            [
                InlineKeyboardButton("🦸Обновить профиль", callback_data='update_profile'),
                InlineKeyboardButton("🕺Показать профиль", callback_data='show_profile'),
            ],
            [InlineKeyboardButton("❌ Удалить данные", callback_data='delete_profile')],
            [InlineKeyboardButton("💘 Назначить свидание", callback_data='date_offer')],
            [InlineKeyboardButton("⏩ Перейти в группу", url='https://t.me/+-LDB4eMeT202YmIy')],
        ]
    else:
        profile = [
            [InlineKeyboardButton("🦸Создать профиль", callback_data='create_profile')],
        ]
    keyboard = [*profile]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Выберите пункт меню:*",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )
