import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware

# Импорты из реквестов
#from app.database.all_requests import clubs as r_clubs
from app.database.all_requests import players as r_players
#from app.database.all_requests import matches as r_matches

import app.keyboards.players_kb as player_kb
import app.keyboards.users_kb as user_kb
from app.states import Admin

router = Router()




# Коллбек отвечает за вывод статистики пользователя как игрока
@router.callback_query(F.data == 'statistic_main_player')
async def handle_statistic_main_player(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    # Находим айди пользователя через его тг-айди
    player_id = await r_players.get_player_id(callback.from_user.id)
    # Данные о всех матчах игрока передаются в переменные
    point_per_attack, point_per_block, point_per_serve = await r_players.get_all_points_player(player_id)
    total_point = point_per_attack + point_per_block + point_per_serve

    # Строим сообщение
    text = (
    f"📊 <b>Ваша статистика</b>\n\n"
    f"<blockquote>"
    f"⚔️ Атака: <b>{point_per_attack}</b>\n"
    f"🧱 Блок: <b>{point_per_block}</b>\n"
    f"🎾 Подача: <b>{point_per_serve}</b>"
    f"</blockquote>\n"
    f"🏆 <b>Всего очков: {total_point}</b>"
    )
    
    # Подставляем в переменную нужные кнопки (для игрока или для обычного пользователя)
    user = await r_players.get_user(callback.from_user.id)
    
    if user.role == "player":
        kb = player_kb.return_to_mm
    else:
        kb = user_kb.return_to_user_mm
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# Колбек отвечает за вывод статистики выбранного пользователем игрока
# Пока не используется, но в будущем пригодится
@router.callback_query(F.data.startswith('player_'))
async def handle_check_statistic_current_player(callback: CallbackQuery, state: FSMContext):
    # Инициализируем переменные для подсчёта статистики в оперативной памяти
    point_per_attack = 0
    point_per_block = 0
    point_per_serve = 0

    # Айди игрока передается через коллбек в переменную
    player_id = int(callback.data.split('_')[-1])
    # Данные о всех матчах игрока передаются в переменную
    all_stat_matches = await r_players.get_all_points_player(player_id)
    
    # Подставляем в переменную нужные кнопки (для игрока или для обычного пользователя)
    user = await r_players.get_user(callback.from_user.id)
    
    if user.role == "player":
        kb = player_kb.return_to_player_mm
    else:
        kb = user_kb.return_to_user_mm

    await callback.answer()
    await callback.message.edit_text(f'Статистика этого игрока:'
                                        f'\nАтака: {all_stat_matches[0]}'
                                        f'\nБлок: {all_stat_matches[1]}'
                                        f'\nПодача: {all_stat_matches[2]}', reply_markup=kb)


