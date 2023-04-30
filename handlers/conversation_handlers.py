from handlers.create_profile import create_profile
from handlers.update_profile import update_profile
from handlers.date_offer import date_offer


CONVERSATION_HANDLERS = [
    create_profile.CREATE_PROFILE_CONVERSATION,
    date_offer.DATE_OFFER_CONVERSATION,
    # update_profile.UPDATE_PROFILE_CONVERSATION,
]
