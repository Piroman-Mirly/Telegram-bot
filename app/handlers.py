import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.middlewares import TestMiddleware
import app.database.requests as request

import app.keyboards as kb

from config import ADMIN


router = Router()

router.message.middleware(TestMiddleware())

# FSM состояния админ-панели
class Admin(StatesGroup):
    # Статус, чтобы удалять весь мусор в сообщениях
    normal = State()
    # Общие статусы
    make_choice = State() # Делает выбор команды перед заходом в админку

    # Статусы для главного админа, доступ к которым даётся конкретному тг-айди
    add_left_club = State() # Добавил первый клуб в матче
    add_right_club = State() # Добавил второй клуб в матче
    add_date = State() # Добавил дату матча

    # Статусы для обычного судьи
    picking_match = State() # Судья выбрал матч
    picking_club = State() # Судья выбрал клуб
    picking_player = State() # Судья выбрал конкретного игрока
    entering_stats = State() # Судья ввёл значения статистики конкретному игроку
    confirming_match = State() # Судья подтвердил значения 

    
    
    
    
    
    
    



# Комманда старт
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # to_enter = await request.set_user(message.from_user.id, message.from_user.first_name)
    await message.answer(f'Привет! Твой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}', reply_markup=kb.return_to_mm)
    # Реализовать одобрение входа / функцию входа, чтобы статистику могли видеть только зарегестрированные пользователи
    # await message.answer('Добро пожаловать, новичок. \nОбновите бота, чтобы использовать весь его функционал')

    await state.set_state(Admin.normal)

# Админ-панель
@router.message(F.text == ADMIN)
async def admin_panel(message: Message, state: FSMContext):
    await message.delete()
    await message.answer('Вы в админ-панеле, выберите действие.', reply_markup=kb.admin_buttons)
    await state.set_state(Admin.make_choice)   

# Удаляет все сообщения, написанные в боте
@router.message(Admin.normal)
async def delete_all_message(message: Message, state: FSMContext):
    await message.delete()
    






# Player statistic callback





# Callbacks



# Коллбек, который отображает главное меню игрока / его профиль
@router.callback_query(F.data == "return_to_player_mm", StateFilter(Admin.normal))
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
@router.callback_query(F.data == "check_all_club", StateFilter(Admin.normal))
async def handle_check_all_club(callback: CallbackQuery):
    await callback.answer()
    # Присваиваем кнопки клубов
    buttons = await kb.clubs(await request.get_all_clubs()) # Взято из request, передает все клубы прямиком из БД
    await callback.message.edit_text(f'Выберите необходимый клуб',
                                        reply_markup=buttons)


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

    await callback.message.edit_text(message, reply_markup=kb.return_to_mm, parse_mode="HTML")

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
                                     f'\nПодача: {all_stat_matches[2]}', reply_markup=kb.return_to_mm)

# Колбек отвечает за вывод статистики выбранного пользователем игрока
@router.callback_query(F.data.startswith('player_'), StateFilter(Admin.normal))
async def hundle_check_statistic_current_player(callback: CallbackQuery):
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
                                        f'\nПодача: {all_stat_matches[2]}', reply_markup=kb.return_to_mm)


# Админка

# Коллбек, который выводит пользователя из состояния админа
@router.callback_query(F.data == 'return_to_player_state')
async def handle_out_of_admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.normal)
    await callback.answer()
    await callback.message.edit_text('Вы вышли из админ-панели', reply_markup=kb.return_to_mm)

# Коллбек, который даёт админу выбрать матч
@router.callback_query(F.data == 'on_statistic_for_match')
async def hundle_add_player_statistic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.picking_match)
    await callback.answer()
    buttons = await kb.matches()
    await callback.message.edit_text('Выберите подходящий матч.', reply_markup=buttons)

# Добавление статистики в конкретный матч
@router.callback_query(F.data.startswith('match_'), StateFilter(Admin.picking_match))
async def handle_add_statis_in_current_match(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.picking_club)
    await callback.answer()

    # Достает объекты клубов из айди матча
    clubs = await request.get_two_club_id_in_match(int(callback.data.split('_')[-1]))

    # Кнопки клубов
    buttons = await kb.clubs(clubs) # Клубы передаются в билдер кнопок


    await callback.message.edit_text('Выберите клуб, статистику игроков которых вы желаете внести:', reply_markup=buttons)



# Показывает всех игроков в данном клубе
@router.callback_query(F.data.startswith('club_'), StateFilter(Admin.picking_club)) # Сработает только в состоянии normal
async def handle_select_current_player(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    buttons = await kb.players(int(callback.data.split('_')[-1]))
    await callback.message.edit_text(f'Выберите игрока, статистику которого вы хотите добавить / изменить:',
                                            reply_markup=buttons)
                                            # В функцию передается разделенный коллбек, из которого извлекается айди клуба
    await state.set_state(Admin.picking_player)