from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.database.requests import get_all_clubs, get_all_players_in_club

# Кнопки в профиле игрока
player_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Статистика', callback_data='statistic_main_player')], [InlineKeyboardButton(text='Клубы', callback_data='check_all_club')], [InlineKeyboardButton(text='Таблица', callback_data='league_table')]
])

# Кнопка возвращает в главный экран игрока
return_to_mm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='На главную', callback_data='return_to_player_mm')]
])

# Кнопки для админ-панели
admin_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить статистику матча', callback_data='add_statistic_for_match')],
    [InlineKeyboardButton(text='Выйти из админ-панели',callback_data='return_to_player_state')]
])


# Билдер, создающий кнопки из N количества данных
async def clubs(): # В данном случае билдер создает кнопки клубов
    all_clubs = await get_all_clubs() # Взято из request, присваивает в качестве значения все клубы из БД
    all_clubs_kb = InlineKeyboardBuilder()

    for club in all_clubs:
        all_clubs_kb.add(InlineKeyboardButton(text=club.name_club, callback_data=f"club_{club.id}"))
    all_clubs_kb.add(InlineKeyboardButton(text='На главную', callback_data='return_to_player_mm'))
    # Возвращает все клубы в виде кнопок
    return all_clubs_kb.adjust(2).as_markup() # adjust отвечает за то, сколько кнопок будет в одном ряду

# Билдер, создающий кнопки из игроков
async def players(club_id):
    all_players = await get_all_players_in_club(club_id) # Взято из request
    all_players_kb = InlineKeyboardBuilder()

    for player in all_players:
        all_players_kb.add(InlineKeyboardButton(text=player.nickname_player, callback_data=f"player_{player.id}"))
    all_players_kb.add(InlineKeyboardButton(text='В меню выбора клубов', callback_data='check_all_club'))
    all_players_kb.add(InlineKeyboardButton(text='На главную', callback_data='return_to_player_mm'))
    # Возвращает всех игроков в клубе в виде кнопок
    return all_players_kb.adjust(1).as_markup()