import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date

from app.middlewares import TestMiddleware
#import app.database.requests as request

import app.keyboards.players_kb as player_kb
import app.keyboards.users_kb as user_kb
from app.states import Admin

# Импорты из реквестов
#from app.database.all_requests import clubs as r_clubs
from app.database.all_requests import players as r_players
from app.database.all_requests import matches as r_matches

router = Router()



# Колбек отвечает за показ расписания на сегодня
# Сделать возможность смотреть расписания на несколько дней вперёд
@router.callback_query(F.data == "schedule_today")
async def get_match_schedule(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    # Берем сегодняшнюю дату
    today = date.today()

    
    
    # Передаются все матчи нужной даты
    all_matches = await r_matches.get_target_date_matches(today)
    if not all_matches:
        # Подставляем в переменную нужные кнопки (для игрока или для обычного пользователя)
        user = await r_players.get_user(callback.from_user.id)
        
        if user.role == "player":
            kb = player_kb.schedule_btn
        else:
            kb = user_kb.schedule_btn
        
        await callback.message.edit_text('На сегодня расписания нет', reply_markup=kb)
        return
    # Подставляем в переменную нужные кнопки (для игрока или для обычного пользователя)
    user = await r_players.get_user(callback.from_user.id)
    
    if user.role == "player":
        kb = await player_kb.match_schedule(all_matches)
    else:
        kb = await user_kb.match_schedule(all_matches)
    await callback.message.edit_text('📅 <b>Расписание на сегодня</b>\n' \
    '<i>Нажмите на матч, чтобы посмотреть детальную информацию о нём</i>', reply_markup=kb, parse_mode="HTML")
