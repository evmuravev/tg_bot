import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from handlers.menu import menu
from handlers.show_profile import show_profile_handler
from handlers.update_profile.common import (
    STEPS,
    get_previous_step
)


logger = logging.getLogger()


async def set_final_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['FINAL_STEP']
):
    await show_profile_handler(update, context)

    options = [
        [
            InlineKeyboardButton("Далее ⏩", callback_data='final_step'),
        ]
    ]

    keyboard = [*options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Так выглядит ваш обновленный профиль\. Нажмите далее\.\.\.",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )

    return step


async def final_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(STEPS['FINAL_STEP'])
    return await previous_step(update, context)


async def final_step(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Продолжаем знакомится! 😉',
    )
    await menu.menu(update, context)

    return ConversationHandler.END
