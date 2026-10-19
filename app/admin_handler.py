from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as request
from app.states import Admin
from config import ADMIN

admin_router = Router()

# Админ-панель
@admin_router.message(F.text == ADMIN)
async def admin_panel(message: Message, state: FSMContext):
    await message.delete()
    await message.answer('Вы в админ-панеле, выберите действие.', reply_markup=kb.admin_buttons)
    await state.set_state(Admin.make_choice)   



# Коллбек, который выводит пользователя из состояния админа
@admin_router.callback_query(F.data == 'return_to_player_state')
async def handle_out_of_admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.normal)
    await callback.answer()
    await callback.message.edit_text('Вы вышли из админ-панели', reply_markup=kb.return_to_mm)


# Коллбек, который даёт админу выбрать матч
@admin_router.callback_query(F.data == 'on_statistic_for_match')
async def hundle_add_player_statistic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.picking_match)
    await callback.answer()
    buttons = await kb.matches()
    await callback.message.edit_text('Выберите подходящий матч.', reply_markup=buttons)


# Добавление статистики в конкретный матч
@admin_router.callback_query(F.data.startswith('match_'), StateFilter(Admin.picking_match))
async def handle_add_statis_in_current_match(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.picking_club)
    await callback.answer()

    # Достает объекты клубов из айди матча
    clubs = await request.get_two_club_id_in_match(int(callback.data.split('_')[-1]))

    # Кнопки клубов
    buttons = await kb.clubs(clubs) # Клубы передаются в билдер кнопок


    await callback.message.edit_text('Выберите клуб, статистику игроков которых вы желаете внести:', reply_markup=buttons)

# Показывает всех игроков в данном клубе
@admin_router.callback_query(F.data.startswith('club_'), StateFilter(Admin.picking_club)) # Сработает только в состоянии normal
async def handle_select_current_player(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    buttons = await kb.players(int(callback.data.split('_')[-1]))
    await callback.message.edit_text(f'Выберите игрока, статистику которого вы хотите добавить / изменить:',
                                            reply_markup=buttons)
                                            # В функцию передается разделенный коллбек, из которого извлекается айди клуба
    await state.set_state(Admin.picking_player)