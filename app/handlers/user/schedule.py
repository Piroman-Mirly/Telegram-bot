import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date

from app.middlewares import TestMiddleware
#import app.database.requests as request

import app.keyboards.keyboards as user_kb
import app.database.requests as request
from app.states import Admin

router = Router()



# Колбек отвечает за показ расписания на сегодня
# Сделать возможность смотреть расписания на несколько дней вперёд
@router.callback_query(F.data == "schedule_today", StateFilter(Admin.normal))
async def get_match_schedule(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    # Берем сегодняшнюю дату
    today = date.today()

    # Передаются все матчи нужной даты
    all_matches = await request.get_target_date_matches(today)
    matches_btn = await user_kb.match_schedule(all_matches)
    await callback.message.edit_text('Расписание на сегодня', reply_markup=matches_btn)
