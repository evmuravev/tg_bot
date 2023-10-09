from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ContextTypes,
)
from db.repositories.date_responses import DateResponseRepository
from db.repositories.profiles import ProfilesRepository
from db.repositories.users import UsersRepository
from db.tasks import get_repository

from handlers.common.users import get_user
from handlers.show_profile import show_profile
from models.date_response import DateResponseCreate
from models.profile import ProfileStatus
from models.user import UserPublic, UserUpdate


async def date_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    if user and user.is_banned:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Вы были забанены и больше не можете совершать действия!',
        )
        return

    if not user or not user.profile or not user.profile.status == ProfileStatus.completed:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Вы еще не создали профиль!\nПерейдите в бот для создания',
        )
        return

    # Проверка на непустой username
    if not update.effective_user.username:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='У вас не заполнен @username (имя пользователя)!',
        )
        return
    else:
        # Обновить username при его несовпадении с базой
        if update.effective_user.username != user.username:
            user_repo = get_repository(UsersRepository, context)
            user = await user_repo.update_username(
                user=UserUpdate(**update.effective_user._get_attrs())
            )
        # Отправка отклика
        profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)
        date_response_repo: DateResponseRepository = get_repository(DateResponseRepository, context)

        inviter = await profile_repo.get_profile_by_user_id(
            user_id=int(update.callback_query.data.split(':')[1])
        )
        responder = await profile_repo.get_profile_by_user_id(
            user_id=update.effective_user.id
        )

        date_response = await date_response_repo.get_date_responses_by_responder(
            responder=responder.id,
            message_id=str(update.effective_message.id)
        )
        if date_response:
            await context.bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                show_alert=True,
                text='Ваш отклик уже был доставлен, дождитесь ответа! 🤞',
            )
        else:
            image, caption = await show_profile(user, context)
            options = [
                [
                    InlineKeyboardButton("✨ Начать общение!", url=f'https://t.me/{update.effective_user.username}'),
                    InlineKeyboardButton("Пожаловаться 😒", callback_data=f'profile_complain:{str(responder.id)}'),
                ]
            ]
            keyboard = [*options]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_photo(
                chat_id=inviter.user_id,
                photo=image.file_id,
                caption='Новый отклик\! ' + caption +'\n\n _Если хотите начать общение, нажмите нужную кнопку!\n\
...Не забудьте напомнить, на какое свидание вы приглашали..._😉',
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )

            # Запись в базу отклика
            date_response_create = DateResponseCreate(
                inviter=inviter.id,
                responder=responder.id,
                message_id=str(update.effective_message.id)
            )
            await date_response_repo.create_date_response(date_response_create=date_response_create)

            await context.bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                show_alert=True,
                text='Ваш отклик с вашим контактом доставлен пользователю!💌\nТеперь он может вам написать🤞',
            )
