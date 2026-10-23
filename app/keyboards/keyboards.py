from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder


from app.database.requests import *

# Кнопки в профиле игрока
player_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Статистика', callback_data='statistic_main_player'), InlineKeyboardButton(text='Статистика всех игроков', callback_data='choice_category_statistic'), InlineKeyboardButton(text='Таблица', callback_data='league_table')]
])

# Возврат в меню игрока
return_to_mm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в профиль', callback_data='return_to_player_mm')]
])
# Возврат к выбору категории статистики или сразу в профиль
return_to_category_statisitc = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в профиль', callback_data='return_to_player_mm'), InlineKeyboardButton(text='К выбору категории', callback_data='choice_category_statistic')]
])

# Кнопки для отображения топ-10 игроков
filter_category = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Топ-10 по атакам', callback_data='top_attack'), InlineKeyboardButton(text='Топ-10 по блокам', callback_data='top_block'), InlineKeyboardButton(text='Топ-10 по подачам', callback_data='top_serve'), InlineKeyboardButton(text='Топ-10 по общему количеству очков', callback_data='top_total')],
    [InlineKeyboardButton(text='Вернуться в профиль', callback_data='return_to_player_mm')]
])

# Копки в таблице
table_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в профиль', callback_data='return_to_player_mm'), InlineKeyboardButton(text='Расписание на сегодня', callback_data='match_schedue'), InlineKeyboardButton(text='Таблица', callback_data='league_table')]
])

# Кнопки для регистрации

# Кнопки для выбора позиции в регистрации
reg_role_buttons = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="ЦБ"), KeyboardButton(text="Доигровщик")],
    [KeyboardButton(text="Связующий"), KeyboardButton(text="Либеро")],
    [KeyboardButton(text="Выход из регистрации")]
])

# Кнопки для подтверждения регистрации
confirm_reg_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Сохранить"), KeyboardButton(text="Изменить роль")],
    [KeyboardButton(text="Отмена")]
])


# Билдеры
# Билдер, создающий расписание матчей в виде кнопок
async def match_schedule():
    all_matches = await get_all_matches() # Взято из request
    all_matches_kb = InlineKeyboardBuilder()

    for match in all_matches:
        left_name_club = await get_name_club(match.left_club_id) # Возвращает имя клуба слева
        right_name_club = await get_name_club(match.right_club_id) # Возвращает имя клуба справа
        all_matches_kb.add(InlineKeyboardButton(text=f'{match.date_match} '
                                                f'{left_name_club} - {right_name_club}',
                                                callback_data=f'match_{match.id}'))
    all_matches_kb.add(InlineKeyboardButton(text='Вернуться в профиль', callback_data='return_to_player_mm'))
    return all_matches_kb.adjust(1).as_markup()