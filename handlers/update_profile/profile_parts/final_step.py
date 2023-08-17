import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from handlers.menu import menu
from handlers.show_profile import show_profile
from handlers.update_profile.common import (
    STEPS
)


logger = logging.getLogger()


async def set_final_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['FINAL_STEP']
):
    await show_profile(update, context)

    options = [
        [
            InlineKeyboardButton("Далее ⏩", callback_data='final_step'),
        ]
    ]

    keyboard = [*options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Так выглядит ваш обновленынй профиль\. Завершаем создание профиля\?*",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )

    return step


async def final_step(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Продолжаем знакомится! 😉',
    )
    await menu.menu(update, context)

    return ConversationHandler.END
