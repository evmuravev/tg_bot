from telegram.ext import CallbackQueryHandler
from handlers.show_profile import (
    show_profile,
)

CALLBACK_QUERY_HANDLERS = [
    CallbackQueryHandler(show_profile, pattern='show_profile'),
]
