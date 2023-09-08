import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes,
)
from core.config import COMPLAIN_TOPIC_ID, TELEGRAM_ADMIN_GROUP_ID
from db.repositories.profiles import ProfilesRepository
from db.repositories.complains import ComplainRepository
from db.repositories.users import UsersRepository
from db.tasks import get_repository
from handlers.delete_profile.delete_profile import delete_profile_and_dates
from handlers.show_profile import show_profile

from handlers.common.users import get_user
from models.complain import ComplainCreate, ComplainStatus, ComplainUpdate
from models.user import UserPublic


logger = logging.getLogger()


async def profile_complain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)

    if user and user.is_banned:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Вы были забанены и больше не можете совершать действия!',
        )
        return

    if not user or not user.profile:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Вы еще не создали профиль!\nПерейдите в бот для создания',
        )
        return

    # Отправка жалобы
    profile_repo = get_repository(ProfilesRepository, context)
    complains_repo = get_repository(ComplainRepository, context)

    complainant = await profile_repo.get_profile_by_user_id(
        user_id=update.effective_user.id
    )
    accused = await profile_repo.get_profile_by_id(
        id=int(update.callback_query.data.split(':')[1])
    )

    complain = await complains_repo.get_complain(
        complainant_id=complainant.id,
        accused_id=accused.id,
    )
    if complain:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Ваша жалоба уже отправлена!',
        )
    else:
        user_repo = get_repository(UsersRepository, context)
        user = await user_repo.get_user_by_id(id=accused.user_id)
        image, caption = await show_profile(user, context)
        options = [
            [
                InlineKeyboardButton(
                    "✔️ Все в порядке!",
                    callback_data=f'profile_complain_decline:{str(accused.id)}:{str(complainant.id)}'
                ),
                InlineKeyboardButton(
                    "❌ Удалить!",
                    callback_data=f'profile_complain_approve:{str(accused.id)}:{str(complainant.id)}'
                ),
            ]
        ]
        keyboard = [*options]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(
                chat_id=TELEGRAM_ADMIN_GROUP_ID,
                photo=image.file_id,
                caption=caption,
                parse_mode="MarkdownV2",
                reply_to_message_id=COMPLAIN_TOPIC_ID,
                reply_markup=reply_markup
        )

        # Запись жалобы в базу
        complain_create = ComplainCreate(
            complainant=complainant.id,
            accused=accused.id,
        )
        await complains_repo.create_complain(complain_create=complain_create)

        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Ваша жалоба отправлена!',
        )


async def profile_complain_decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile_repo = get_repository(ProfilesRepository, context)
    accused_id = update.callback_query.data.split(':')[1]
    complainant_id = update.callback_query.data.split(':')[2]
    complainant_profile = await profile_repo.get_profile_by_id(
        id=int(complainant_id)
    )
    accused_profile = await profile_repo.get_profile_by_id(
        id=int(accused_id)
    )
    await context.bot.send_message(
        chat_id=complainant_profile.user_id,
        text=f'Ваша жалоба на профиль "{accused_profile.name}, {accused_profile.city}" \
была рассмотрена, но ничего предосудительного мы не обнаружили! \
Спасибо за бдительность!',
    )

    # Закрываем жалобу - меням статус в БД
    complains_repo: ComplainRepository = get_repository(ComplainRepository, context)
    complain = await complains_repo.get_complain(
        complainant_id=int(complainant_id),
        accused_id=int(accused_id),
    )
    if complain:
        complain_update = complain.copy(update={'status': ComplainStatus.declined})
        await complains_repo.update_status_complain(complain_update=complain_update)

    # Удаляем сообщение из админской группы
    try:
        await context.bot.delete_message(
            chat_id=TELEGRAM_ADMIN_GROUP_ID,
            message_id=update.effective_message.message_id
        )
    except BadRequest as ex:
        logger.warning(ex)


async def profile_complain_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)
    accused_id = update.callback_query.data.split(':')[1]
    complainant_id = update.callback_query.data.split(':')[2]
    complainant_profile = await profile_repo.get_profile_by_id(
        id=int(complainant_id)
    )
    accused_profile = await profile_repo.get_profile_by_id(
        id=int(accused_id)
    )
    # Удаляем профиль и свидания
    user_repo: UsersRepository = get_repository(UsersRepository, context)
    user = await user_repo.get_user_by_id(id=accused_profile.user_id)
    await delete_profile_and_dates(user, context)

    # Обвиняемому напихиваем в панамку
    updated_user = await user_repo.inc_num_of_complains(user=user)
    # Если панамка не выдерживает, то в бан!
    if updated_user.num_of_complains > 1:
        await user_repo.update_is_banned(user=updated_user)
        await context.bot.send_message(
            chat_id=accused_profile.user_id,
            text='Нам очень жаль, за повторное нарушение вы были забанены!',
        )
    else:
        await context.bot.send_message(
            chat_id=accused_profile.user_id,
            text='За неподобающее содержание Ваше свидание и профиль были удалены! Повторное нарушение приведет вас к бану!',
        )

    # Обвинителю выписываем медаль
    await context.bot.send_message(
        chat_id=complainant_profile.user_id,
        text=f'Ваша жалоба на профиль "{accused_profile.name}, {accused_profile.city}" \
была рассмотрена - нарушитель наказан! \
Спасибо за бдительность!',
    )

    # Закрываем жалобу - меням статус в БД
    complains_repo: ComplainRepository = get_repository(ComplainRepository, context)
    complain = await complains_repo.get_complain(
        complainant_id=int(complainant_id),
        accused_id=int(accused_id),
    )
    if complain:
        complain_update = complain.copy(update={'status': ComplainStatus.approved})
        await complains_repo.update_status_complain(complain_update=complain_update)

    # Удаляем сообщение из админской группы
    try:
        await context.bot.delete_message(
            chat_id=TELEGRAM_ADMIN_GROUP_ID,
            message_id=update.effective_message.message_id
        )
    except BadRequest as ex:
        logger.warning(ex)
