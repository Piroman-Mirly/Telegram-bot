from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.database.requests import get_all_clubs, get_all_players_in_club, get_all_matches, get_name_club

# Кнопки в профиле игрока
player_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Статистика', callback_data='statistic_main_player')], [InlineKeyboardButton(text='Статистика всех игроков', callback_data='choice_category_statistic')], [InlineKeyboardButton(text='Таблица', callback_data='league_table')]
])

# Возврат в меню игрока
return_to_mm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в профиль', callback_data='return_to_player_mm')]
])
# Возврат к выбору категории статистики или сразу в профиль
return_to_category_statisitc = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в профиль', callback_data='return_to_player_mm')], [InlineKeyboardButton(text='К выбору категории', callback_data='choice_category_statistic')]
])
# Кнопки для отображения топ-10 игроков
filter_category = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Топ-10 по атакам', callback_data='top_attack')], [InlineKeyboardButton(text='Топ-10 по блокам', callback_data='top_block')], [InlineKeyboardButton(text='Топ-10 по подачам', callback_data='top_serve')],
    [InlineKeyboardButton(text='Топ-10 по общему количеству очков', callback_data='top_total')],
    [InlineKeyboardButton(text='Вернуться в профиль', callback_data='return_to_player_mm')]
])

# Кнопки для админ-панели
# Для главного экрана
admin_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить статистику матча', callback_data='on_statistic_for_match')],
    [InlineKeyboardButton(text='Выйти из админ-панели',callback_data='return_to_player_state')]
])

admin_return_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выйти из админ-панели', callback_data='return_to_player_state')]
])





# Билдер, создающий кнопки из N количества данных
async def clubs(clubs): # В данном случае билдер создает кнопки клубов
    all_clubs = clubs # На вход подаются строки клуба
    all_clubs_kb = InlineKeyboardBuilder()

    for club in all_clubs:
        all_clubs_kb.add(InlineKeyboardButton(text=club.name_club, callback_data=f"club_{club.id}"))
    # Если клуба два, то запрос идёт из админки и нужно дать другую кнопку для возврата в меню
    if len(clubs) == 2:
        all_clubs_kb.add(InlineKeyboardButton(text='Назад', callback_data='on_statistic_for_match'))
    else:
        all_clubs_kb.add(InlineKeyboardButton(text='На главную', callback_data='return_to_player_mm'))
    # Возвращает все клубы в виде кнопок
    return all_clubs_kb.adjust(2).as_markup() # adjust отвечает за то, сколько кнопок будет в одном ряду

# Создает кнопки из двух нужных клубов, которые участвовали в матче
async def clubs_in_match(id_left_club, id_right_club):
    button_clubs = InlineKeyboardBuilder()



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
    # Для возможности вернуться в окно выбора матча
    #all_matches_kb.add(InlineKeyboardButton(text='Вернуться к выбору матча', callback_data='on_statistic_for_match'))
    return all_matches_kb.adjust(1).as_markup()