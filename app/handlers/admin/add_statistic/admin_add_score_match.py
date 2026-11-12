from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импорты из самого бота
from app.states import Admin
import app.keyboards.admin_kb as adm_kb

# Импорты из реквестов
from app.database.all_requests import clubs as r_clubs
#from app.database.all_requests import players as r_players
from app.database.all_requests import matches as r_matches

# Роутер для админ-панели
admin_router = Router()

# Для клуба, играющего дома
@admin_router.callback_query(F.data == 'add_score_match')
async def pick_left_score(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    data = await state.get_data()

    # Получаем айди матча из FSM
    match_id = data['match_id']

    # Получаем данные матча, чтобы узнать имя клуба
    match = await r_matches.get_match_by_id(match_id)

    left_name = await r_clubs.get_club_name(match.left_club_id)

    await callback.message.edit_text(
        f"Сколько партий взял домашний клуб ({left_name})?",
        reply_markup=adm_kb.set_score_kb(match_id, "left", left_name)
    )

# Для клуба, играющего на выезде
@admin_router.callback_query(F.data.startswith('setscore_'))
async def pick_right_score(callback: CallbackQuery, state: FSMContext):

    _, match_id, side, score = callback.data.split('_')
    match_id = int(match_id)
    score = int(score)
    
    if side == "left":
        await callback.answer()
        await state.update_data(score_left=score)
        
        match = await r_matches.get_match_by_id(match_id)
        right_name = await r_clubs.get_club_name(match.right_club_id)
        
        await callback.message.edit_text(
            f"Теперь сколько партий взял гостевой клуб ({right_name})?",
            reply_markup=adm_kb.set_score_kb(match_id, "right", right_name)
        )
    else: # Подтверждение счёта, если: side == "right"
        await state.update_data(score_right=score)
        data = await state.get_data()

        # Безопасно достаем значение (если его нет, вернется None)
        score_left = data.get('score_left')
        score_right = data.get('score_right')

        if score_left is not None and score_left == score_right:
            await callback.answer("❌ В волейболе не может быть ничьей! Счёт по партиям должен быть разным.", 
            show_alert=True)
            return
        
        match = await r_matches.get_match_by_id(match_id)
        left_name = await r_clubs.get_club_name(match.left_club_id)
        right_name = await r_clubs.get_club_name(match.right_club_id)
        
        text = (
            f"<b>Проверьте счёт матча:</b>\n"
            f"{left_name} <b>{data['score_left']} - {data['score_right']}</b> {right_name}"
        )
        
        # Тут понадобится кнопка "Подтвердить" и "Отмена"
        kb = InlineKeyboardBuilder()
        kb.button(text='Подтвердить', callback_data=f'confirm_score_{match_id}')
        kb.button(text='Отмена', callback_data=f'match_{match_id}')
        
        await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

# Запись данных в БД
@admin_router.callback_query(F.data.startswith('confirm_score_'))
async def save_match_score(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    
    match_id = data['match_id']
    score_left = data['score_left']
    score_right = data['score_right']
    
    # Определяем победителя
    winner_id = None
    if score_left > score_right:
        winner_id = await r_clubs.get_left_club_id(match_id) # Напиши функцию
    elif score_right > score_left:
        winner_id = await r_clubs.get_right_club_id(match_id) # Напиши функцию

    # Написать функцию для изменения матча
    await r_matches.update_match_score(match_id, score_left, score_right, winner_id)
    
    await callback.message.edit_text(
        "Счёт успешно сохранён!", 
        reply_markup=await adm_kb.back_to_matches(match_id)
    )









    

