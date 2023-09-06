from telegram.ext import CommandHandler
from handlers.show_profile import (
    show_profile_handler
)
from handlers.menu import menu
from handlers.start import start


COMMAND_HANDLERS = [
    CommandHandler("start", start.start),
    CommandHandler("menu", menu.menu),
    CommandHandler("show_profile", show_profile_handler)
]
