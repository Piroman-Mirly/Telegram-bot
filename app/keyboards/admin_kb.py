from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импорты из реквестов
from app.database.all_requests import clubs as r_clubs
#from app.database.all_requests import players as r_players
#from app.database.all_requests import matches as r_matches

# Для главного экрана
admin_buttons = InlineKeyboardMarkup(inline_keyboard=[ 
    [InlineKeyboardButton(text='Добавить данные матча', callback_data='view_all_scheduled_matches')],
    [InlineKeyboardButton(text='Добавить матч', callback_data='add_new_match')], 
    [InlineKeyboardButton(text='Выйти из админ-панели',callback_data='return_to_player_state')]
])

# Кнопки в матче
admin_selected_match = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить счёт встречи', callback_data='add_score_match')],
    [InlineKeyboardButton(text='Добавить статистику игрока', callback_data='add_statistic_for_match')], 
    [InlineKeyboardButton(text='Закрыть матч для изменения', callback_data='switch_status_to_finished')], 
    [InlineKeyboardButton(text='К матчам', callback_data='view_all_scheduled_matches'), InlineKeyboardButton(text='В меню', callback_data='to_mm_admin_panel')]
])

# Кнопка для выхода из админ панели
admin_return_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выйти из админ-панели', callback_data='return_to_player_state')]
])

# Кнопка для возвращения в главный экран админ-панели
to_mm_admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='В главное меню админ-панели', callback_data='to_mm_admin_panel')]
])

# Кнопки для возвращения в меню добавления статистики
# Вернуться к выбору игроков
back_to_players = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='К списку игроков', callback_data='back_to_players')]
])
# Вернуться к выбору клубов
back_to_clubs = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='К списку клубов', callback_data='add_statistic_for_match')]
])


# Кнопка для подтверждения статистики
succses_statistic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить', callback_data='succses_statistic'), InlineKeyboardButton(text='К списку игроков', callback_data='back_to_players')]
])

# Кнопки для подтверждения создания матча
confirm_create_match_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить', callback_data='confirm_data_match')],
    [InlineKeyboardButton(text='Начать сначала', callback_data='add_new_match')]                                                                                         
])

# Билдеры
# Билдер, который спрашивает, уверен ли пользователь в том, чтобы изменить статус текущему матчу
async def confirm_switch_matched(match_id):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Подтвердить', callback_data="switch_status_current_match"))
    kb.add(InlineKeyboardButton(text='Назад', callback_data=f"match_{match_id}"))
    return kb.adjust(1).as_markup()

# Билдер создает кнопки клубов
async def clubs(clubs, match_id): 
    all_clubs = clubs # На вход подаются строки клуба
    all_clubs_kb = InlineKeyboardBuilder()

    for club in all_clubs:
        all_clubs_kb.add(InlineKeyboardButton(text=club.name_club, callback_data=f"club_{club.id}"))

    all_clubs_kb.add(InlineKeyboardButton(text='К матчу', callback_data=f'match_{match_id}'))
    # Возвращает все клубы в виде кнопок
    return all_clubs_kb.adjust(2).as_markup() # adjust отвечает за то, сколько кнопок будет в одном ряду

# Билдер, создающий кнопки из игроков, у которых ещё нет статистики в матче
async def list_players(players):
    all_players_kb = InlineKeyboardBuilder()

    if not players:
        all_players_kb.button(text="К выбору клубов", callback_data="add_statistic_for_match")
        return all_players_kb.as_markup()

    for player in players:
        all_players_kb.add(InlineKeyboardButton(text=player.nickname_player, callback_data=f"player_{player.id}"))
    # Возвращает пользователя в меню, где нужно выбирать клубы
    all_players_kb.add(InlineKeyboardButton(text='К списку клубов', callback_data='add_statistic_for_match'))
    
    # Возвращает всех игроков в клубе в виде кнопок
    return all_players_kb.adjust(1).as_markup()

# Билдер, создающий список всех матчей в виде кнопок
async def matches(matches):
    all_matches = matches # Передает все нужные матчи
    all_matches_kb = InlineKeyboardBuilder()

    for count, match in enumerate(all_matches, start = 1):
        left_name_club = await r_clubs.get_club_name(match.left_club_id) # Возвращает имя клуба слева
        right_name_club = await r_clubs.get_club_name(match.right_club_id) # Возвращает имя клуба справа
        all_matches_kb.add(InlineKeyboardButton(text=f'{count}. '
                                                f'{left_name_club} {match.score_left} - {match.score_right} {right_name_club}',
                                                callback_data=f'match_{match.id}'))
    all_matches_kb.add(InlineKeyboardButton(text='Вернуться в главное меню админ-панели', callback_data='to_mm_admin_panel'))
    return all_matches_kb.adjust(1).as_markup()

def set_score_kb(match_id : int, side: str, club_name : str):
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{club_name} — 0 партий", callback_data=f"setscore_{match_id}_{side}_0")
    kb.button(text=f"{club_name} — 1 партия", callback_data=f"setscore_{match_id}_{side}_1")
    kb.button(text=f"{club_name} — 2 партии", callback_data=f"setscore_{match_id}_{side}_2")
    kb.button(text=f"{club_name} — 3 партии", callback_data=f"setscore_{match_id}_{side}_3")
    
    kb.button(text="Назад к матчу", callback_data=f"match_{match_id}")
    kb.adjust(1)
    return kb.as_markup()


# Билдер для возврата в карточку матча
async def back_to_matches(match_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='К матчу', callback_data=f'match_{match_id}'))
    kb.adjust(1)
    return kb.as_markup()
