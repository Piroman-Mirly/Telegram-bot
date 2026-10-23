from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_all_clubs, get_all_players_in_club, get_all_matches, get_name_club

# Для главного экрана
admin_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить статистику матча', callback_data='on_statistic_for_match'), InlineKeyboardButton(text='Добавить матч', callback_data='add_new_match')],
    [InlineKeyboardButton(text='Выйти из админ-панели',callback_data='return_to_player_state')]
])

# Кнопка для выхода из админ панели
admin_return_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выйти из админ-панели', callback_data='return_to_player_state')]
])

# Кнопка для возвращения в главный экран админ-панели
to_mm_admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в главное меню админ-панели', callback_data='to_mm_admin_panel')]
])

# Кнопки для подтверждения создания матча
confirm_create_match_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить', callback_data='confirm_data_match')],
    [InlineKeyboardButton(text='Начать сначала', callback_data='add_new_match')]                                                                                         
])

# Билдеры
# Билдер создает кнопки клубов
async def clubs(clubs): 
    all_clubs = clubs # На вход подаются строки клуба
    all_clubs_kb = InlineKeyboardBuilder()

    for club in all_clubs:
        all_clubs_kb.add(InlineKeyboardButton(text=club.name_club, callback_data=f"club_{club.id}"))
    # Если клуба два, то запрос идёт из админки и нужно дать другую кнопку для возврата в меню
    if len(clubs) == 2:
        all_clubs_kb.add(InlineKeyboardButton(text='Назад', callback_data='on_statistic_for_match'))
    else:
        # Пока что эта функция используется только в админке, поэтому кнопка "на главную" будет возвращать в меню админки
        all_clubs_kb.add(InlineKeyboardButton(text='На главную', callback_data='to_mm_admin_panel'))
    # Возвращает все клубы в виде кнопок
    return all_clubs_kb.adjust(2).as_markup() # adjust отвечает за то, сколько кнопок будет в одном ряду

# Билдер, создающий кнопки из игроков
async def players(club_id):
    all_players = await get_all_players_in_club(club_id) # Взято из request
    all_players_kb = InlineKeyboardBuilder()

    for player in all_players:
        all_players_kb.add(InlineKeyboardButton(text=player.nickname_player, callback_data=f"player_{player.id}"))
    all_players_kb.add(InlineKeyboardButton(text='На главную', callback_data='on_statistic_for_match'))
    # Возвращает всех игроков в клубе в виде кнопок
    return all_players_kb.adjust(1).as_markup()

# Билдер, создающий список всех матчей в виде кнопок
async def matches():
    all_matches = await get_all_matches() # Взято из request
    all_matches_kb = InlineKeyboardBuilder()

    for match in all_matches:
        left_name_club = await get_name_club(match.left_club_id) # Возвращает имя клуба слева
        right_name_club = await get_name_club(match.right_club_id) # Возвращает имя клуба справа
        all_matches_kb.add(InlineKeyboardButton(text=f'{match.id}.'
                                                f'{left_name_club} {match.score_left} - {match.score_right} {right_name_club}',
                                                callback_data=f'match_{match.id}'))
    all_matches_kb.add(InlineKeyboardButton(text='Вернуться в главное меню админ-панели', callback_data='to_mm_admin_panel'))
    return all_matches_kb.adjust(1).as_markup()
