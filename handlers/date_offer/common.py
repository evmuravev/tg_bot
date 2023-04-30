import handlers.date_offer.date_offer_parts as part

from typing import Coroutine
from telegram import Update
from telegram.ext import ContextTypes


STEPS = {
    'WHERE': 0,
    'WHEN': 1,
    'EXPECTATIONS': 2,
    'BILL_SPLITTING': 3,
    'FINAL_STEP': 4
}


def get_next_step(current_step: int) -> Coroutine[Update, ContextTypes, int]:
    next_steps_map = {
        STEPS['WHERE']: part.when.set_when_step,
        STEPS['WHEN']: part.expectations.set_excpectations_step,
        STEPS['EXPECTATIONS']: part.bill_splitting.set_bill_splitting_step,
        STEPS['BILL_SPLITTING']: part.final_step.set_final_step,
    }
    return next_steps_map[current_step]


def get_previous_step(current_step: int) -> Coroutine[Update, ContextTypes, int]:
    previous_steps_map = {
        STEPS['WHEN']: part.where.set_where_step,
        STEPS['EXPECTATIONS']: part.when.set_when_step,
        STEPS['BILL_SPLITTING']: part.expectations.set_excpectations_step,
        STEPS['FINAL_STEP']: part.bill_splitting.set_bill_splitting_step,
    }

    return previous_steps_map[current_step]
