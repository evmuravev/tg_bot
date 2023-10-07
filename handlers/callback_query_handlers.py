from telegram.ext import CallbackQueryHandler
from handlers.show_profile import (
    show_profile_handler,
)
from handlers.date_response import (
    date_response,
    date_response_clicked_through
)
from handlers.complains import (
    date_complain,
    date_complain_approve,
    date_complain_decline,
    date_profile_complain_approve,
    profile_complain,
    profile_complain_approve,
    profile_complain_decline
)

CALLBACK_QUERY_HANDLERS = [
    CallbackQueryHandler(show_profile_handler, pattern='show_profile'),
    CallbackQueryHandler(date_response, pattern='lets_go\:.*'),
    CallbackQueryHandler(date_response_clicked_through, pattern='is_clicked_through\:.*'),
    CallbackQueryHandler(date_complain, pattern='date_complain\:.*'),
    CallbackQueryHandler(date_complain_approve, pattern='date_complain_approve\:.*'),
    CallbackQueryHandler(date_complain_decline, pattern='date_complain_decline\:.*'),
    CallbackQueryHandler(date_profile_complain_approve, pattern='date_profile_complain_approve\:.*'),
    CallbackQueryHandler(profile_complain, pattern='profile_complain\:.*'),
    CallbackQueryHandler(profile_complain_approve, pattern='profile_complain_approve\:.*'),
    CallbackQueryHandler(profile_complain_decline, pattern='profile_complain_decline\:.*'),
]
