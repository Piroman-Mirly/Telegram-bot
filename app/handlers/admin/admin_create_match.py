from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# Импорты из самого бота
from app.states import Admin
import app.keyboards.admin_kb as adm_kb
import app.database.requests as request

from datetime import datetime


# Роутер для админ-панели
admin_router = Router()


# Коллбек, который позволяет админу начать создавать матч
@admin_router.callback_query(F.data == 'add_new_match')
async def handle_add_match_to_admin_panel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.set_date)
    await callback.message.edit_text('Давайте создадим матч!\n'
    'Введите дату матча в формате ДД.ММ.ГГГГ, например: 01.01.2025', reply_markup=adm_kb.to_mm_admin_panel)


# Бот ожидает дату
@admin_router.message(Admin.set_date)
async def handle_get_date_match(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        # Парсим строку в объект date
        match_date = datetime.strptime(text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer('Неверный формат! Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n'
        'Пример: 01.01.2025', reply_markup=adm_kb.to_mm_admin_panel)
        return
    # Сохранение данных в оперативную память FSM состояний
    await state.update_data(date = match_date)
    await state.set_state(Admin.choice_left_club)
    buttons_clubs = await adm_kb.clubs(await request.get_all_clubs())
    await message.answer('Выберите клуб, который играл на домашнем поле', reply_markup=buttons_clubs)


# Ловушка, если пользователь пишет текст вместо нажатия на инлайн-кнопку
@admin_router.message(Admin.choice_left_club)
async def trap_left_club(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, выберите клуб, нажав на одну из кнопок выше')


# Айди первого клуба заносится в оперативную память, вбот предлагает выбрать второй клуб
@admin_router.callback_query(F.data.startswith('club_'), StateFilter(Admin.choice_left_club))
async def claim_left_club(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    buttons_clubs = await adm_kb.clubs(await request.get_all_clubs())
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
        buttons_clubs = await adm_kb.clubs(await request.get_all_clubs())
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
    f'Гостевой клуб: {right_club}', reply_markup=adm_kb.confirm_create_match_btn)

# Данные записываются в БД
@admin_router.callback_query(F.data == 'confirm_data_match')
async def confirm_create_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    await request.create_new_match(data['date'], data['left_club'], data['right_club'])


    await callback.message.edit_text('Данные успешно сохранены', reply_markup=adm_kb.to_mm_admin_panel)
    await state.clear()

