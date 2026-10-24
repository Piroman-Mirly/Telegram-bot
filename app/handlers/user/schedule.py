import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware
#import app.database.requests as request

import app.keyboards.keyboards as user_kb
from app.states import Admin

router = Router()



# Колбек отвечает за показ расписания на сегодня
# Сделать возможность смотреть расписания на несколько дней вперёд
@router.callback_query(F.data == "match_schedue", StateFilter(Admin.normal))
async def get_match_schedule(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    all_matches = await user_kb.match_schedule()
    await callback.message.edit_text('Расписание на сегодня', reply_markup=all_matches)
