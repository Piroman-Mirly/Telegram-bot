import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
#from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware
import app.database.requests as request

import app.keyboards.keyboards as user_kb
from app.states import Admin

router = Router()



# Коллбек отвечает за отрисовку таблицы в отсортированном виде
@router.callback_query(F.data == "league_table", StateFilter(Admin.normal))
async def handle_table_league(callback: CallbackQuery):
    await callback.answer()
    # Из файла request данные о текущих местах клуба передаются в переменную
    places_in_table = await request.get_data_for_table_clubs()

    # Отправная точка для создания единого сообщения
    head = ["Место", "Название", "Кол-во побед", "Кол-во очков"]

    # Итоговое сообщение
    lines = []

    # Цикл for с enumerate вытаскивает из таблицы данные в формате (place, (id, name_club, wins, points))
    # Сам place является счетчиком места
    for place, rows in enumerate(places_in_table, start = 1):
        _, name_club, points, wins = rows
        # Собираем в один массив данные клубов добавля новые клубы в каждом цикле
        lines.append([str(place), name_club, str(wins), str(points)])

    # Считаем максимальную ширину каждой колонки
    # Читается как: максимум по всем строкам длины i-й ячейки
    widths = [max(len(head[i]), max(len(line[i]) for line in lines)) for i in range(len(head))]

    # Функция форматирования строки с отступом
    def format_lines(cells):
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    # Собирается сообщение
    all_lines = [format_lines(head)]
    for line in lines:
        all_lines.append(format_lines(line))

    # Разделяем итоговый массив "переходом на новую строку" (\n)
    message = "<pre>" + "\n".join(all_lines) + "</pre>"

    await callback.message.edit_text(message, reply_markup=user_kb.table_button, parse_mode="HTML")

