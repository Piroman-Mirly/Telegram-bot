from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as request
from app.states import Registration

regist_router = Router()

# Запускается процесс регистрации  

# После ввода никнейма бот просит выбрать позицию на поле с помощью кнопок
@regist_router.message(Registration.nickname)
async def await_role_handler(message: Message, state: FSMContext):
    # Сохраняем имя в оперативную память FSM состояний
    await state.update_data(nickname = message.text, tg_id = message.from_user.id)
    
    await message.answer('Теперь укажите вашу позицию на поле', reply_markup=kb.reg_role_buttons)

    await state.set_state(Registration.await_role)


# Пользователь подвтерждает данные, которые ввёл
@regist_router.message(Registration.await_role, F.text.in_({"ЦБ", "Доигровщик", "Связующий", "Либеро"}))
async def choose_role(message: Message, state: FSMContext):
    # Все данные регистрации передаются в одну переменную
    await state.update_data(role = message.text)
    data = await state.get_data()

    await message.answer(f'Проверьте ваши данные:\n\n'
                         f'Ник: {data.get('nickname')}\n'
                         f'Позиция: {data.get('role')}\n'
                         f'Сохранить?',
                         reply_markup=kb.confirm_reg_kb)

    await state.set_state(Registration.confirm_reg)


# Выход из регистрации на этапе выбора роли
@regist_router.message(Registration.await_role, F.text == "Выход из регистрации")
async def cancel_from_role(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Регистрация отменена.", reply_markup=ReplyKeyboardRemove())

# Если пользователь напишет что-то не то во время выбора позиции, то ему прилетит предупреждение
@regist_router.message(Registration.await_role, F.text)
async def trap_role(message: Message):
    await message.answer("Пожалуйста, выберите позицию с помощью кнопок ниже")

# Подтверждение и запись данных в БД
@regist_router.message(Registration.confirm_reg, F.text == "Сохранить")
async def save_data(message: Message, state: FSMContext):
    data = await state.get_data()
    await request.create_player(data['tg_id'], data['nickname'], data['role'])
    await message.answer(
        f"Готово! Ник: {data['nickname']}, позиция: {data['role']}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

# Изменение позиции
@regist_router.message(Registration.confirm_reg, F.text == "Изменить роль")
async def change_role(message: Message, state: FSMContext):
    await message.answer("Выберите новую позицию:", reply_markup=kb.reg_role_buttons)
    await state.set_state(Registration.await_role)

# Отмена регистрации
@regist_router.message(Registration.confirm_reg, F.text == "Отмена")
async def cancel_confirm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Регистрация отменена", reply_markup=ReplyKeyboardRemove())

# Если пользователь напишет что-то не то во время подтверждения данных, то поймает предупреждение
@regist_router.message(Registration.confirm_reg, F.text)
async def trap_confirm(message: Message):
    await message.answer("Пожалуйста, нажмите «Сохранить», «Изменить роль» или «Отмена»")