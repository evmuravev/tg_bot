from telegram.ext import CommandHandler
from handlers.show_profile import (
    show_profile
)
from handlers.menu import menu
from handlers.start import start
from handlers.update_profile import (
    update_profile
)


COMMAND_HANDLERS = [
    CommandHandler("start", start.start),
    CommandHandler("menu", menu.menu),
    CommandHandler("update_profile", update_profile.update_profile),
    CommandHandler("show_profile", show_profile)
]
