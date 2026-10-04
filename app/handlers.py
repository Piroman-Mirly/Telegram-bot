import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware
import app.database.requests as request

import app.keyboards as kb


router = Router()

router.message.middleware(TestMiddleware())

# FSM состояния
class Join(StatesGroup):
    pass


# Комманда старт
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # to_enter = await request.set_user(message.from_user.id, message.from_user.first_name)
    await message.answer(f'Привет! Твой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}', reply_markup=kb.return_to_mm)
    # Реализовать одобрение входа / функцию входа, чтобы статистику могли видеть только зарегестрированные пользователи
    # await message.answer('Добро пожаловать, новичок. \nОбновите бота, чтобы использовать весь его функционал')

        
    






# Player statistic callback





# Callbacks

# Коллбек, котоырй отображает главное меню игрока / его профиль
@router.callback_query(F.data == "return_to_player_mm")
async def handle_return_to_player_mm(callback : CallbackQuery):
    await callback.answer()
    data_player = await request.get_statistic_current_player(callback.from_user.id)
    # Меняет последний текст бота на статистику игрока.
    await callback.message.edit_text(f'———Главный экран———'
                                     f'\nВаш игровой ник: {data_player.nickname_player}'
                                     f'\nАйди клуба: {data_player.club_id}' # Поменять на название
                                     f'\nВаша позиция: {data_player.role}'
                                     f'\nВаш трансферный статус: {data_player.transfer_status}',
                                     reply_markup=kb.player_kb)

# Отображает все клубы в виде Inline кнопок
@router.callback_query(F.data == "check_all_club")
async def handle_check_all_club(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(f'Выберите необходимый клуб',
                                        reply_markup=await kb.clubs())

# Показывает всех игроков в данном клубе
@router.callback_query(F.data.startswith('club_'))
async def handle_check_current_club(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(f'Игроки, играющие в этом клубе:',
                                            reply_markup= await kb.players(int(callback.data.split('_')[1])))
                                            # В функцию передается раделенный коллбек, из которого извлекается айди клуба

# Коллбек отвечает за отрисовку таблицы в отсортированном виде
@router.callback_query(F.data == "league_table")
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
        club_id, name_club, points, wins = rows
        # Собираем в один массив данные клубов добавля новые клубы в каждом цикле
        lines.append([str(place), name_club, str(wins), str(points)])

    # Считаем максимальную ширину каждой колонки
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



    await callback.message.edit_text(message, reply_markup=kb.return_to_mm, parse_mode="HTML")