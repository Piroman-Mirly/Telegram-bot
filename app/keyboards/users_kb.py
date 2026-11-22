from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder


# Импорты из реквестов
from app.database.all_requests import clubs as r_clubs
#from app.database.all_requests import players as r_players
#from app.database.all_requests import matches as r_matches

# Кнопки для подачи заявки на вступление, или же просмотр каких-либо активностей
main_player_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏆 Топ-10', callback_data='choice_category_statistic'), InlineKeyboardButton(text='📋 Таблица', callback_data='league_table')],
    [InlineKeyboardButton(text='📝 Подать заявку на вступление', callback_data='apply_for_player')]
])

# Возврат в меню пользователя
return_to_mm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 На главную', callback_data='return_to_user_mm')]
])

# Кнопки для отображения топ-10 игроков
filter_category = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⚔️ Атака', callback_data='top_attack'), InlineKeyboardButton(text='🧱 Блок', callback_data='top_block'), InlineKeyboardButton(text='🎾 Подача', callback_data='top_serve'), InlineKeyboardButton(text='🏆 Всего', callback_data='top_total')],
    [InlineKeyboardButton(text='🔙 На главную', callback_data='return_to_user_mm')]
])

# Возврат к выбору категории статистики или сразу в профиль
return_to_category_statisitc = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏆 К категориям', callback_data='choice_category_statistic')],
    [InlineKeyboardButton(text='🔙 На главную', callback_data='return_to_user_mm')]
])

# Копки в таблице
table_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📅 Расписание на сегодня', callback_data='schedule_today')],
    [InlineKeyboardButton(text='🔙 На главную', callback_data='return_to_user_mm')]
])

# Кнопки расписания
schedule_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📋 Таблица', callback_data='league_table')],
    [InlineKeyboardButton(text='🔙 На главную', callback_data='return_to_user_mm')]
    
])

# Кнопки в подробном инфо о матче
detail_schedule_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📋 Таблица', callback_data='league_table')],
    [InlineKeyboardButton(text='📅 К расписанию', callback_data='schedule_today')],
    [InlineKeyboardButton(text='🔙 На главную', callback_data='return_to_user_mm')]
])

# Билдеры

# Билдер, создающий расписание матчей в виде кнопок
async def match_schedule(matches): # Передается кортеж матчей
    all_matches = matches
    all_matches_kb = InlineKeyboardBuilder()

    for match in all_matches:
        left_name_club = await r_clubs.get_club_name(match.left_club_id) # Возвращает имя клуба слева
        right_name_club = await r_clubs.get_club_name(match.right_club_id) # Возвращает имя клуба справа
        all_matches_kb.add(InlineKeyboardButton(text=f'{match.date_match} '
                                                f'{left_name_club} - {right_name_club}',
                                                callback_data=f'schedule_match_info_{match.id}'))
    all_matches_kb.add(InlineKeyboardButton(text='📋 Таблица', callback_data='league_table'))
    all_matches_kb.add(InlineKeyboardButton(text='🔙 На главную', callback_data='return_to_user_mm'))
    return all_matches_kb.adjust(1).as_markup()