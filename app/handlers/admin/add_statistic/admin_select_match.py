from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


# Импорты из самого бота
from app.states import Admin
import app.keyboards.admin_kb as adm_kb

# Импорты из реквестов
from app.database.all_requests import clubs as r_clubs
from app.database.all_requests import players as r_players
from app.database.all_requests import matches as r_matches

# Роутер для админ-панели
admin_router = Router()

# Показывает список незаполненных матчей для внесения статистики
@admin_router.callback_query(F.data == 'view_all_scheduled_matches')
async def handle_view_all_scheduled_matches(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    all_matches = await r_matches.schedule_matches()

    if not all_matches:
        await callback.message.edit_text('Все матчи заполнены', reply_markup=adm_kb.to_mm_admin_panel)

    all_matches_kb = await adm_kb.matches(all_matches)

    await callback.message.edit_text('Выберите матч, статистику которого вы хотите изменить', reply_markup=all_matches_kb)
    await state.set_state(Admin.picking_match)

# Отображение карточки выбранного матча
@admin_router.callback_query(F.data.startswith('match_'))
async def handle_add_statistic_in_current_match(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.picking_club)
    await callback.answer()

    # Айди матча
    match_id = int(callback.data.split('_')[-1])
    # Данные матча
    match = await r_matches.get_match_by_id(match_id)

    # Запоминает айди выбранного матча
    await state.update_data(match_id = match_id)
    count_filled, count_total = await r_players.get_all_count_players(match_id)

    # Названия клубов
    l_club_name = await r_clubs.get_club_name(match.left_club_id)
    r_club_name = await r_clubs.get_club_name(match.right_club_id)

    status = 'Заполнен' if match.status == 'finished' else 'Не заполнен'

    await callback.message.edit_text(f'ID: {match.id}, Дата: {match.date_match}\n'
                                     f'Статус: {status}\n'
                                     f'{l_club_name} {match.score_left or 0} - {match.score_right or 0} {r_club_name}\n\n'
                                     f'Заполнено статистики игроков: {count_filled} из {count_total}', reply_markup=adm_kb.admin_selected_match)

    await state.set_state(Admin.make_choice)

