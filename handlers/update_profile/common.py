import handlers.update_profile.profile_parts as part

from typing import Coroutine
from telegram import Update
from telegram.ext import ContextTypes


STEPS = {
    'NAME': 1,
    'SEX': 2,
    'AGE': 3,
    'REGION': 41,
    'CITY': 42,
    'IMAGE': 5,
    'BIO': 6,
    'FINAL_STEP': 7
}


def get_next_step(current_step: int) -> Coroutine[Update, ContextTypes, int]:
    next_steps_map = {
        STEPS['NAME']: part.sex.set_sex_step,
        STEPS['SEX']: part.age.set_age_step,
        STEPS['AGE']: part.city.set_city_step,
        STEPS['CITY']: part.image.set_image_step,
        STEPS['IMAGE']: part.bio.set_bio_step,
        STEPS['BIO']: part.final_step.set_final_step,
    }
    return next_steps_map[current_step]


def get_previous_step(current_step: int) -> Coroutine[Update, ContextTypes, int]:
    previous_steps_map = {
        STEPS['SEX']: part.name.set_name_step,
        STEPS['AGE']: part.sex.set_sex_step,
        STEPS['CITY']: part.age.set_age_step,
        STEPS['IMAGE']: part.city.set_city_step,
        STEPS['BIO']: part.image.set_image_step,
        STEPS['FINAL_STEP']: part.bio.set_bio_step,
    }

    return previous_steps_map[current_step]
