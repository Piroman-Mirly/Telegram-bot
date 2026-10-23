from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as request
from app.states import Admin
from config import ADMIN

from datetime import datetime

admin_router = Router()

# Админ-панель
@admin_router.message(F.text == ADMIN)
async def admin_panel(message: Message, state: FSMContext):
    await message.delete()
    await message.answer('Вы в админ-панеле, выберите действие.', reply_markup=kb.admin_buttons)

# Меню админки через коллбек
@admin_router.callback_query(F.data == 'to_mm_admin_panel')
async def admin_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Вы в админ-панеле, выберите действие.', reply_markup=kb.admin_buttons)



# Коллбек, который выводит пользователя из состояния админа
@admin_router.callback_query(F.data == 'return_to_player_state')
async def handle_out_of_admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.normal)
    await callback.answer()
    await callback.message.edit_text('Вы вышли из админ-панели\n'
    'Нажмите кнопку, чтобы использовать его как обычный пользователь', reply_markup=kb.return_to_mm)

# Создание матча
# Коллбек, который позволяет админу начать создавать матч
@admin_router.callback_query(F.data == 'add_new_match')
async def handle_add_match_to_admin_panel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.set_date)
    await callback.message.edit_text('Давайте создадим матч!\n'
    'Введите дату матча в формате ДД.ММ.ГГГГ, например: 01.01.2025', reply_markup=kb.to_mm_admin_panel)

# Бот ожидает дату
@admin_router.message(Admin.set_date)
async def handle_get_date_match(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        # Парсим строку в объект date
        match_date = datetime.strptime(text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer('Неверный формат! Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n'
        'Пример: 01.01.2025', reply_markup=kb.to_mm_admin_panel)
        return
    # Сохранение данных в оперативную память FSM состояний
    await state.update_data(date = match_date)
    await state.set_state(Admin.choice_left_club)
    buttons_clubs = await kb.clubs(await request.get_all_clubs())
    await message.answer('Выберите клуб, который играл на домашнем поле', reply_markup=buttons_clubs)
    

# Ловушка, если пользователь пишет текст вместо нажатия на инлайн-кнопку
@admin_router.message(Admin.choice_left_club)
async def trap_left_club(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, выберите клуб, нажав на одну из кнопок выше. 👆')
    

# Айди первого клуба заносится в оперативную память, вбот предлагает выбрать второй клуб
@admin_router.callback_query(F.data.startswith('club_'), StateFilter(Admin.choice_left_club))
async def claim_left_club(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    buttons_clubs = await kb.clubs(await request.get_all_clubs())
    club_id = int(callback.data.split("_")[1])
    await state.update_data(left_club=club_id)
    await callback.message.edit_text('Первый клуб выбран, теперь выберите второй', reply_markup=buttons_clubs)

    await state.set_state(Admin.choice_right_club)

# Второй клуб выбирается и бот ждёт подтверждения, чтобы сохранить данные
@admin_router.callback_query(F.data.startswith('club_'), StateFilter(Admin.choice_right_club))
async def claim_right_club(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    club_id = int(callback.data.split("_")[1])
    data = await state.get_data()

    # Если первый и второй клуб похожи, то будет выведена ошибка
    if data.get('left_club') == club_id:
        buttons_clubs = await kb.clubs(await request.get_all_clubs())
        await callback.message.edit_text('Один и тот же клуб не может играть против себя!\n' \
        'Выберите первый клуб ещё раз', reply_markup=buttons_clubs)
        await state.set_state(Admin.choice_left_club)
        return
    
    await state.update_data(right_club=club_id)

    data = await state.get_data()

    # Названия двух клубов
    left_club = await request.get_name_club(data.get('left_club'))
    right_club = await request.get_name_club(data.get('right_club'))

    await callback.message.edit_text(f'Матч создан, проверьте данные:\n\n' \
    f'Дата: {data.get('date')}\n'
    f'Домашний клуб: {left_club}\n'
    f'Гостевой клуб: {right_club}', reply_markup=kb.confirm_create_match_btn)

# Данные записываются в БД
@admin_router.callback_query(F.data == 'confirm_data_match')
async def confirm_create_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    await request.create_new_match(data['date'], data['left_club'], data['right_club'])


    await callback.message.edit_text('Данные успешно сохранены', reply_markup=kb.to_mm_admin_panel)
    await state.clear()








# Коллбек, который даёт админу выбрать матч
@admin_router.callback_query(F.data == 'on_statistic_for_match')
async def hundle_add_player_statistic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.picking_match)
    await callback.answer()
    buttons = await kb.matches()
    await callback.message.edit_text('Выберите подходящий матч', reply_markup=buttons)


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