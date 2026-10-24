import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware
import app.database.requests as request

import app.keyboards.keyboards as user_kb
from app.states import Admin

router = Router()




# Коллбек отвечает за вывод статистики пользователя как игрока
@router.callback_query(F.data == 'statistic_main_player', StateFilter(Admin.normal))
async def handle_statistic_main_player(callback: CallbackQuery):
    # Инициализируем переменные для подсчёта статистики в оперативной памяти
    point_per_attack = 0
    point_per_block = 0
    point_per_serve = 0

    # Находим айди пользователя через его тг-айди
    player_id = await request.get_player_id(callback.from_user.id)
    # Данные о всех матчах игрока передаются в переменную
    all_stat_matches = await request.get_all_points_player(player_id)



    await callback.answer()
    await callback.message.edit_text(f'Ваша статистика:'
                                     f'\nАтака: {all_stat_matches[0]}'
                                     f'\nБлок: {all_stat_matches[1]}'
                                     f'\nПодача: {all_stat_matches[2]}', reply_markup=user_kb.return_to_mm)

# Колбек отвечает за вывод статистики выбранного пользователем игрока
# Пока не используется, но в будущем пригодится
@router.callback_query(F.data.startswith('player_'), StateFilter(Admin.normal))
async def handle_check_statistic_current_player(callback: CallbackQuery):
    # Инициализируем переменные для подсчёта статистики в оперативной памяти
    point_per_attack = 0
    point_per_block = 0
    point_per_serve = 0

    # Айди игрока передается через коллбек в переменную
    player_id = int(callback.data.split('_')[-1])
    # Данные о всех матчах игрока передаются в переменную
    all_stat_matches = await request.get_all_points_player(player_id)


    await callback.answer()
    await callback.message.edit_text(f'Статистика этого игрока:'
                                        f'\nАтака: {all_stat_matches[0]}'
                                        f'\nБлок: {all_stat_matches[1]}'
                                        f'\nПодача: {all_stat_matches[2]}', reply_markup=user_kb.return_to_mm)


