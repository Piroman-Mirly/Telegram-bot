from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# Импорты из самого бота
from app.states import Admin
import app.keyboards.admin_kb as adm_kb
import app.database.requests as request




# Роутер для админ-панели
admin_router = Router()

# Коллбек, который даёт админу выбрать матч для заполнения статистики
@admin_router.callback_query(F.data == 'on_statistic_for_match')
async def hundle_add_player_statistic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.picking_match)
    await callback.answer()
    buttons = await adm_kb.matches()
    await callback.message.edit_text('Выберите подходящий матч', reply_markup=buttons)

# Добавление статистики в конкретный матч
@admin_router.callback_query(F.data.startswith('match_'), StateFilter(Admin.picking_match))
async def handle_add_statis_in_current_match(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.picking_club)
    await callback.answer()

    # Достает объекты клубов из айди матча
    clubs = await request.get_two_club_id_in_match(int(callback.data.split('_')[-1]))

    # Кнопки клубов
    buttons = await adm_kb.clubs(clubs) # Клубы передаются в билдер кнопок


    await callback.message.edit_text('Выберите клуб, статистику игроков которых вы желаете внести:', reply_markup=buttons)


# Показывает всех игроков в данном клубе
@admin_router.callback_query(F.data.startswith('club_'), StateFilter(Admin.picking_club)) # Сработает только в состоянии normal
async def handle_select_current_player(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    buttons = await adm_kb.players(int(callback.data.split('_')[-1]))
    await callback.message.edit_text(f'Выберите игрока, статистику которого вы хотите добавить / изменить:',
                                            reply_markup=buttons)
                                            # В функцию передается разделенный коллбек, из которого извлекается айди клуба
    await state.set_state(Admin.picking_player)

