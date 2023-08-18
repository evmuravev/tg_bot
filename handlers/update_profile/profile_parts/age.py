import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.repositories.profiles import ProfilesRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.update_profile.common import (
    STEPS,
    get_next_step,
)
from models.profile import ProfileUpdate
from models.user import UserPublic


logger = logging.getLogger()


async def set_age_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step=STEPS['AGE']
):
    user: UserPublic = await get_user(update, context)
    age = str(user.profile.age)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"*Ваш возраст \- {age}:*\n_\(укажите исправление или нажмите  /skip ⏩ \)_",
        parse_mode="MarkdownV2",
    )
    return step


async def set_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    age = update.message.text
    if age.isnumeric() and 16 <= int(age) <= 100:
        age = int(update.message.text)
        match age:
            case 16:
                left = 16
                right = 20
            case 100:
                left = 85
                right = 100
            case _:
                left = max(age//10*10, 16)
                right = min(age//10*10+10, 100)
        age_tag = f'#от_{left}_до_{right}'
    elif age.isnumeric() and int(age) < 16:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Ваш возраст должен быть больше 16 🚫',
        )
        return await set_age_step(update, context)
    elif age.isnumeric() and int(age) > 100:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Максимально возможный возраст - 100 лет 🚫',
        )
        return await set_age_step(update, context)
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Неправильно задан возраст!\nУкажите свой реальный возраст цифрами',
        )
        return await set_age_step(update, context)

    profile_repo: ProfilesRepository = get_repository(ProfilesRepository, context)
    profile_update = {
        'age': age,
        'age_tag': age_tag
    }
    await profile_repo.update_profile(
        profile_update=ProfileUpdate(**profile_update),
        user_id=user.id
    )

    next_step = get_next_step(STEPS['AGE'])
    return await next_step(update, context)


async def age_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(STEPS['AGE'])
    return await next_step(update, context)
