from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импорты из самого бота
from app.states import Admin
import app.keyboards.admin_kb as adm_kb

# Импорты из реквестов
#from app.database.all_requests import clubs as r_clubs
#from app.database.all_requests import players as r_players
from app.database.all_requests import matches as r_matches

# Роутер для админ-панели
admin_router = Router()

# Бот спрашивает, действительно ли нужно менять статус матча на "Завершен" 
@admin_router.callback_query(F.data == "switch_status_to_finished")
async def handle_y_or_n_to_finished_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    match_id = data['match_id']

    await callback.message.edit_text('Вы уверены, что хотите завершить заполнение данного матча?\n'
    'Внимание! Если вы измение статус матча, то вы больше не сможете изменить его статистику', reply_markup=await adm_kb.confirm_switch_matched(match_id))

# Меняет статус матча на "Завершен"
@admin_router.callback_query(F.data == "switch_status_current_match")
async def handle_confirmed_switch_status_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    match_id = data['match_id']

    await r_matches.update_status_match(match_id)

    await callback.message.edit_text('Статус матча успешно изменён!', reply_markup=adm_kb.to_mm_admin_panel)