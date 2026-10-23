from aiogram import F, Router
# Пока ниче не надо
# from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# Импорты из самого бота
import app.keyboards.admin_kb as adm_kb
import app.keyboards.keyboards as user_kb
from app.states import Admin
from config import ADMIN

# Роутер для админ-панели
admin_router = Router()

# Админ-панель
@admin_router.message(F.text == ADMIN)
async def admin_panel(message: Message, state: FSMContext):
    await message.delete()
    await message.answer('Вы в админ-панеле, выберите действие.', reply_markup=adm_kb.admin_buttons)

# Меню админки через коллбек
@admin_router.callback_query(F.data == 'to_mm_admin_panel')
async def admin_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Вы в админ-панеле, выберите действие.', reply_markup=adm_kb.admin_buttons)



# Коллбек, который выводит пользователя из состояния админа
@admin_router.callback_query(F.data == 'return_to_player_state')
async def handle_out_of_admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.normal)
    await callback.answer()
    await callback.message.edit_text('Вы вышли из админ-панели\n'
    'Нажмите кнопку, чтобы использовать бота как обычный пользователь', reply_markup=user_kb.return_to_mm)
