from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импорты из самого бота
from app.states import Admin
import app.keyboards.admin_kb as adm_kb
import app.database.requests as request




# Роутер для админ-панели
admin_router = Router()

# Показывает матчи, в который необходимо добавить счёт
@admin_router.callback_query(F.data == 'add_score_match')
async def handle_picked_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.picking_match_for_score)

    # Матчи, которым необходимо заполнить счёт
    current_matches = await request.none_score_matches()

    # Если матчей нет
    if not current_matches:
        await callback.message.edit_text('Все матчи уже имеют счёт', reply_markup=adm_kb.to_mm_admin_panel)
        return

    kb = InlineKeyboardBuilder()


    # Создаем кнопки прямо тут
    for m in current_matches:
        # Сделать так, чтобы в самом реквесте появлялась табличка с именами клубов, чтобы брать их оттуда, а не делать запросы
        left_club_name = await request.get_club_name(m.left_club_id)
        right_club_name = await request.get_club_name(m.right_club_id)
        kb.button(text=f'{m.date_match} | {left_club_name} - {right_club_name}', callback_data=f'setmatch_{m.id}')
    kb.button(text='Назад', callback_data='to_mm_admin_panel')
    kb.adjust(1)
    
    await callback.message.edit_text('Выберите матч для ввода счёта:', reply_markup=kb.as_markup())

# Для клуба, играющего дома
@admin_router.callback_query(F.data.startswith('setmatch_'), StateFilter(Admin.picking_match_for_score))
async def pick_left_score(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    match_id = int(callback.data.split('_')[1])

    await state.update_data(match_id = match_id)

    # Получаем данные матча, чтобы узнать имя клуба
    match = await request.get_match_by_id(match_id)

    left_name = await request.get_name_club(match.left_club_id)

    await callback.message.edit_text(
        f"Матч #{match_id}\nСколько партий взял домашний клуб ({left_name})?",
        reply_markup=adm_kb.set_score_kb(match_id, "left", left_name)
    )

# Для клуба, играющего на выезде
@admin_router.callback_query(F.data.startswith('setscore_'), StateFilter(Admin.picking_match_for_score))
async def pick_right_score(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _, match_id, side, score = callback.data.split('_')
    match_id = int(match_id)
    score = int(score)
    
    if side == "left":
        await state.update_data(score_left=score)
        
        match = await request.get_match_by_id(match_id)
        right_name = await request.get_name_club(match.right_club_id)
        
        await callback.message.edit_text(
            f"Теперь сколько партий взял гостевой клуб ({right_name})?",
            reply_markup=adm_kb.set_score_kb(match_id, "right", right_name)
        )
    else: # Подтверждение счёта, если: side == "right"
        await state.update_data(score_right=score)
        data = await state.get_data()
        
        match = await request.get_match_by_id(match_id)
        left_name = await request.get_name_club(match.left_club_id)
        right_name = await request.get_name_club(match.right_club_id)
        
        text = (
            f"<b>Проверьте счёт матча:</b>\n"
            f"{left_name} <b>{data['score_left']} - {data['score_right']}</b> {right_name}"
        )
        
        # Тут понадобится кнопка "Подтвердить" и "Отмена"
        kb = InlineKeyboardBuilder()
        kb.button(text='Подтвердить', callback_data=f'confirm_score_{match_id}')
        kb.button(text='Отмена', callback_data='back_to_matches_for_score')
        
        await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
        await state.set_state(Admin.confirming_score)

# Запись данных в БД
@admin_router.callback_query(F.data.startswith('confirm_score_'), StateFilter(Admin.confirming_score))
async def save_match_score(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    
    match_id = data['match_id']
    score_left = data['score_left']
    score_right = data['score_right']
    
    # Определяем победителя
    winner_id = None
    if score_left > score_right:
        winner_id = await request.get_left_club_id(match_id) # Напиши функцию
    elif score_right > score_left:
        winner_id = await request.get_right_club_id(match_id) # Напиши функцию

    # Написать функцию для изменения матча
    await request.update_match_score(match_id, score_left, score_right, winner_id)
    await state.clear()
    
    await callback.message.edit_text(
        "Счёт успешно сохранён!", 
        reply_markup=adm_kb.to_mm_admin_panel
    )









    

