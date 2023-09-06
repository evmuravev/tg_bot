import logging
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)

from db.tasks import get_repository
from db.repositories.profiles import ProfilesRepository
from models.profile import ProfileCreate, ProfileStatus, ProfilePublic
from models.user import UserPublic
from handlers.create_profile.profile_parts import (
    name, sex, age, city, image, bio, cancel, username, final_step
)
from handlers.create_profile.common import STEPS
from handlers.common.users import get_user, register_new_user


logger = logging.getLogger()


async def create_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    if not user:
        user = await register_new_user(update, context)

    match user:
        case UserPublic(username=None):
            return await username.set_username_step(update, context)
        case UserPublic(profile=ProfilePublic(status=ProfileStatus.completed)):
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text='Ваш профиль уже существует! \nВы можете обновить профиль, если пожелаете!',
            )
            return
        case UserPublic(profile=None) | UserPublic(profile=ProfilePublic(status=ProfileStatus.deleted)):
            if user.is_banned:
                await context.bot.answer_callback_query(
                    callback_query_id=update.callback_query.id,
                    show_alert=True,
                    text='Вы были забанены и больше не можете создавать профиль!',
                )
                return
            profile_repo = get_repository(ProfilesRepository, context)
            profile_create = ProfileCreate(user_id=user.id)
            user.profile = await profile_repo.create_profile_for_user(
                profile_create=profile_create
            )
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text='🙌 Ура! Профиль успешно создан. \nДавайте его заполним!',
                reply_markup=ReplyKeyboardRemove(),

            )
        case UserPublic(profile=ProfilePublic(name=None)):
            return await name.set_name_step(update, context)
        case UserPublic(profile=ProfilePublic(sex=None)):
            return await sex.set_sex_step(update, context)
        case UserPublic(profile=ProfilePublic(age=None)):
            return await age.set_age_step(update, context)
        case UserPublic(profile=ProfilePublic(city=None)):
            return await city.set_city_step(update, context)
        case UserPublic(profile=ProfilePublic(image=None)):
            return await image.set_image_step(update, context)
        case UserPublic(profile=ProfilePublic(bio=None)):
            return await bio.set_bio_step(update, context)
        case UserPublic(profile=ProfilePublic(status=ProfileStatus.partially_completed)):
            return await final_step.set_final_step(update, context)
    return await name.set_name_step(update, context)


CREATE_PROFILE_CONVERSATION = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CommandHandler('create_profile', create_profile),
        CallbackQueryHandler(create_profile, pattern='create_profile')],

    states={
        STEPS['USERNAME']: [
            CallbackQueryHandler(username.set_username, pattern='^set_username$')
        ],
        STEPS['NAME']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, name.set_name)
        ],
        STEPS['SEX']: [
            CallbackQueryHandler(sex.set_sex),
            CommandHandler('back', sex.sex_back)
        ],
        STEPS['AGE']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, age.set_age),
            CommandHandler('back', age.age_back),
        ],
        STEPS['REGION']: [
            CallbackQueryHandler(city.set_region, pattern='^[^(next|prev)]+'),
            CallbackQueryHandler(city.region_pagination_callback, pattern='(next|prev)_region'),
            CommandHandler('back', city.city_back),
        ],
        STEPS['CITY']: [
            CallbackQueryHandler(city.set_city, pattern='^[^(next|prev|back)]+'),
            CallbackQueryHandler(city.city_pagination_callback, pattern='(next|prev)_city'),
            CallbackQueryHandler(city.back_to_regions_callback, pattern='back_to_regions'),
            CommandHandler('back', city.city_back),
        ],
        STEPS['IMAGE']: [
            MessageHandler(filters.PHOTO, image.set_image),
            CommandHandler('back', image.image_back),
        ],
        STEPS['BIO']: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, bio.set_bio),
            CommandHandler('back', bio.bio_back),
        ],
        STEPS['FINAL_STEP']: [
            CallbackQueryHandler(final_step.start_over, pattern='start_over'),
            CallbackQueryHandler(final_step.final_step, pattern='final_step'),
        ],
    },

    fallbacks=[CommandHandler('cancel', cancel.cancel)],
)
