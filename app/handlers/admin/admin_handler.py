from aiogram import F, Router
# Пока ниче не надо
# from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# Импорты из самого бота
import app.keyboards.admin_kb as adm_kb
import app.keyboards.players_kb as player_kb
from app.states import Admin
from config import ADMIN

#Импорты из реквестов
#from app.database.all_requests import clubs as r_clubs
from app.database.all_requests import players as r_players
#from app.database.all_requests import matches as r_matches

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
    'Нажмите кнопку, чтобы использовать бота как обычный пользователь', reply_markup=player_kb.return_to_mm)

@admin_router.callback_query(F.data.startswith('approve_'))
async def handle_approve_user(callback: CallbackQuery):
    await callback.answer()
    
    # Достаем ID пользователя из калбека
    target_tg_id = int(callback.data.split('_')[-1])
    
    # Меняем роли в БД
    await r_players.change_user_role(target_tg_id, 'player')
    
    # Пишем пользователю, что он принят
    try:
        await callback.bot.send_message(
            chat_id=target_tg_id,
            text="🎉 Поздравляем! Ваша заявка одобрена.\nТеперь вам доступна регистрация как игрока. Нажмите /start, чтобы обновить меню."
        )
    except Exception:
        pass # Если пользователь заблокировал бота, мы просто игнорируем ошибку

    # Меняем текст сообщения у админа (чтобы он видел, что заявка обработана)
    await callback.message.edit_text(
        f"✅ Пользователь <code>{target_tg_id}</code> одобрен.", 
        parse_mode="HTML"
    )

# Ловим нажатие на кнопку "Отклонить"
@admin_router.callback_query(F.data.startswith('reject_'))
async def handle_reject_user(callback: CallbackQuery):
    await callback.answer()
    target_tg_id = int(callback.data.split('_')[-1])
    
    # Пишем пользователю об отказе
    try:
        await callback.bot.send_message(
            chat_id=target_tg_id,
            text="😔 К сожалению, ваша заявка на вступление была отклонена администратором."
        )
    except Exception:
        pass

    await callback.message.edit_text(
        f"❌ Пользователь <code>{target_tg_id}</code> отклонен.", 
        parse_mode="HTML"
    )