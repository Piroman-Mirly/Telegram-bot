import asyncio
from itertools import zip_longest
import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date

from app.middlewares import TestMiddleware
#import app.database.requests as request

import app.keyboards.keyboards as user_kb
from app.states import Admin

# Импорты из реквестов
from app.database.all_requests import clubs as r_clubs
from app.database.all_requests import players as r_players
from app.database.all_requests import matches as r_matches

router = Router()

@router.callback_query(F.data.startswith('match_info_'), StateFilter(Admin.normal))
async def handle_show_match_details(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    # Получаем айди матча
    match_id = int(callback.data.split('_')[-1])

    # 1) Получаем данные матча
    match = await r_matches.get_match_by_id(match_id)

    if not match:
        await callback.message.edit_text('Матч не найден', reply_markup=user_kb.detail_schedule_button)
        return
    
    # 2) Получаем названия клубов
    left_name = await r_clubs.get_club_name(match.left_club_id)
    right_name = await r_clubs.get_club_name(match.right_club_id)

    # 3) Получаем составы команд
    left_players = await r_players.get_all_players_in_club(match.left_club_id)
    right_players = await r_players.get_all_players_in_club(match.right_club_id)

    # 4) Формируем текст подробного расписания

    text = "📅 <b>Анонс матча</b>\n\n"
    text += f"🏐 <b>{left_name}</b>  vs  <b>{right_name}</b>\n\n"

    # 4.1) Создаем шапку таблицы
    # {left_name[:13]:<15} обрезает имя до 13 символов и добивает пробелами до 15
    table = f"<b>{left_name[:13]:<15} | {right_name[:13]}</b>\n"
    table += "─" * 32 + "\n" # Линия-разделитель

    # zip_longest идет по парам: (игрок1_лево, игрок1_право)
    for l_player, r_player in zip_longest(left_players, right_players, fillvalue=None):
        # Если игрок есть в паре "Левый_клуб - Правый_клуб", то берём его ник, если нет - ставим пустую строку (fillvalue)
        l_name = l_player.nickname_player[:13] if l_player else ""
        r_name = r_player.nickname_player[:13] if r_player else ""

        # Добавляем маркер в виде закрашенной точки

        table += f"• {l_name:<13} | • {r_name}\n"

    # Оборачиваем в <pre>, чтобы шрифт был моноширинным (колонки не съедут)
    text = f"<pre>{table}</pre>"

    # 5) Отправка сообщения 
    await callback.message.edit_text(
        text, 
        reply_markup=user_kb.detail_schedule_button, # Кнопка "Назад к расписанию"
        parse_mode="HTML"
    )

