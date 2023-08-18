from telegram.ext import CallbackQueryHandler
from handlers.show_profile import (
    show_profile,
)
from handlers.date_response_complain import (
    date_response,
    date_complain
)

CALLBACK_QUERY_HANDLERS = [
    CallbackQueryHandler(show_profile, pattern='show_profile'),
    CallbackQueryHandler(date_response, pattern=r'lets_go\:.*'),
    CallbackQueryHandler(date_complain, pattern=r'complain\:.*'),
]
