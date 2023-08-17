import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)
from handlers.update_profile.profile_parts import (
    name, sex, age, city, image, bio, cancel, final_step
)
from handlers.create_profile.common import STEPS


logger = logging.getLogger()


async def update_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await name.set_name_step(update, context)


UPDATE_PROFILE_CONVERSATION = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CommandHandler('update_profile', update_profile),
        CallbackQueryHandler(update_profile, pattern='update_profile')],

    states={
        STEPS['NAME']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, name.set_name),
            CommandHandler('skip', name.name_skip),
        ],
        STEPS['SEX']: [
            CallbackQueryHandler(sex.set_sex),
            CommandHandler('skip', sex.sex_skip),
        ],
        STEPS['AGE']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, age.set_age),
            CommandHandler('skip', age.age_skip),
        ],
        STEPS['REGION']: [
            CallbackQueryHandler(city.set_region, pattern='^[^(next|prev)]+'),
            CallbackQueryHandler(city.region_pagination_callback, pattern='(next|prev)_region'),
            CommandHandler('skip', city.city_skip),
        ],
        STEPS['CITY']: [
            CallbackQueryHandler(city.set_city, pattern='^[^(next|prev|back)]+'),
            CallbackQueryHandler(city.city_pagination_callback, pattern='(next|prev)_city'),
            CallbackQueryHandler(city.back_to_regions_callback, pattern='back_to_regions'),
            CommandHandler('skip', city.city_skip),
        ],
        STEPS['IMAGE']: [
            MessageHandler(filters.PHOTO, image.set_image),
            CommandHandler('skip', image.image_skip),
        ],
        STEPS['BIO']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, bio.set_bio),
            CommandHandler('skip', bio.bio_skip),
        ],
        STEPS['FINAL_STEP']: [
            CallbackQueryHandler(final_step.final_step, pattern='final_step'),
        ],
    },

    fallbacks=[CommandHandler('cancel', cancel.cancel)],
)
