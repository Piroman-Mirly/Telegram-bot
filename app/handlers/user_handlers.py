import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.middlewares import TestMiddleware
import app.database.requests as request

import app.keyboards.keyboards as user_kb
from app.states import Admin, Registration

router = Router()

router.message.middleware(TestMiddleware())
    



# Комманда старт
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Admin.normal)

    data_player = await request.get_statistic_current_player(message.from_user.id)

    # Если вернули None, то значит такого пользователя нет и начинается регистрация
    if not data_player:
        await message.answer('Новый пользователь! Давайте зарегестрируемся.\nВведите ваш игровой ник')
        await state.set_state(Registration.nickname)
        return


    # В будущем переделать на один запрос с JOIN
    club_name = await request.get_club_name(data_player.club_id)
    await message.answer(f'———Главный экран———'
                                     f'\nВаш игровой ник: {data_player.nickname_player}'
                                     f'\nНазвание клуба: {club_name}'
                                     f'\nВаша позиция: {data_player.role}'
                                     f'\nВаш трансферный статус: {data_player.transfer_status}',
                                     reply_markup=user_kb.player_kb)
    

# Удаляет все сообщения, написанные в боте
@router.message(Admin.normal)
async def delete_all_message(message: Message, state: FSMContext):
    await message.delete()


# Callbacks

# Коллбек, который отображает главное меню игрока / его профиль
@router.callback_query(F.data == "return_to_player_mm", StateFilter(Admin.normal))
async def handle_return_to_player_mm(callback : CallbackQuery):
    await callback.answer()
    data_player = await request.get_statistic_current_player(callback.from_user.id)
    # В будущем переделать на один запрос с JOIN
    club_name = await request.get_club_name(data_player.club_id)
    # Меняет последний текст бота на статистику игрока.
    await callback.message.edit_text(f'———Главный экран———'
                                     f'\nВаш игровой ник: {data_player.nickname_player}'
                                     f'\nНазвание клуба: {club_name}'
                                     f'\nВаша позиция: {data_player.role}'
                                     f'\nВаш трансферный статус: {data_player.transfer_status}',
                                     reply_markup=user_kb.player_kb)

# Отображает все клубы в виде Inline кнопок
@router.callback_query(F.data == "check_all_club", StateFilter(Admin.normal))
async def handle_check_all_club(callback: CallbackQuery):
    await callback.answer()
    # Присваиваем кнопки клубов
    buttons = await user_kb.clubs(await request.get_all_clubs()) # Взято из request, передает все клубы прямиком из БД
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

    await callback.message.edit_text(message, reply_markup=user_kb.table_button, parse_mode="HTML")

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

# Колбек, который переносит пользователя в окно выбора категории для показа статистики топ-10
@router.callback_query(F.data == 'choice_category_statistic', StateFilter(Admin.normal))
async def handle_make_choice_category_statistic_top_10_players(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Выберите категорию статистики', reply_markup=user_kb.filter_category)



# Колбек отвечает за вывод статистики всех игроков
@router.callback_query(F.data.startswith("top_"), StateFilter(Admin.normal))
async def handle_top_players_statistic(callback: CallbackQuery):
    await callback.answer()

    # Из callback'а достаём категорию: "top_attack" → "attack"
    category = callback.data.split("_")[1]

    # Список кортежей в формате: [(ник, клуб, атака, блок, подача, всего очков)] с лимитом в 10 игроков
    top = await request.get_top_players(category=category, limit=10)

    # Переводим в человекочитаемый заголовок
    titles = {
        "attack": "⚔️ Топ-10 по атаке",
        "block":  "🧱 Топ-10 по блоку",
        "serve":  "🎾 Топ-10 по подаче",
        "total":  "🏆 Топ-10 по общим очкам",
    }
    # Если нет статистики, то бот предупредит
    if not top:
        await callback.message.edit_text("Статистики пока нет.", reply_markup=user_kb.return_to_mm)
        return

    # Создается текст для вывода топ-10
    lines = [f"<b>{titles.get(category, 'Топ-10')}</b>\n"]


    # Цикл, который создает топ-10 игроков по ка тегории
    for place, row in enumerate(top, start=1):
        nickname, club_name, attack, block, serve, total = row

        # Значение, по которому сортируем, — подсветим жирным
        values = {"attack": attack, "block": block, "serve": serve, "total": total}
        highlight = values.get(category, total)

        lines.append(
            f"{place}. <b>{nickname}</b> ({club_name}) — <b>{highlight}</b>\n"
            f"   ⚔️ {attack} | 🧱 {block} | 🎾 {serve} | 🏆 {total}"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=user_kb.return_to_category_statisitc,
        parse_mode="HTML",
    )


# Колбек отвечает за показ расписания на сегодня
# Сделать возможность смотреть расписания на несколько дней вперёд
@router.callback_query(F.data == "match_schedue", StateFilter(Admin.normal))
async def get_match_schedule(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    all_matches = await user_kb.match_schedule()
    await callback.message.edit_text('Выберите подходящий матч', reply_markup=all_matches)