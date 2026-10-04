import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware
import app.database.requests as request

import app.keyboards as kb


router = Router()

router.message.middleware(TestMiddleware())

# FSM состояния
class Join(StatesGroup):
    pass


# Комманда старт
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # to_enter = await request.set_user(message.from_user.id, message.from_user.first_name)
    await message.answer(f'Привет! Твой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}', reply_markup=kb.return_to_mm)
    # Реализовать одобрение входа / функцию входа, чтобы статистику могли видеть только зарегестрированные пользователи
    # await message.answer('Добро пожаловать, новичок. \nОбновите бота, чтобы использовать весь его функционал')

        
    




# Callbacks

# Player statistic callback







# Коллбек, котоырй отображает главное меню игрока / его профиль
@router.callback_query(F.data == "return_to_player_mm")
async def handle_return_to_player_mm(callback : CallbackQuery):
    await callback.answer()
    data_player = await request.get_statistic_current_player(callback.from_user.id)
    # Меняет последний текст бота на статистику игрока.
    await callback.message.edit_text(f'———Главный экран———'
                                     f'\nВаш игровой ник: {data_player.nickname_player}'
                                     f'\nАйди клуба: {data_player.club_id}' # Поменять на название
                                     f'\nВаша позиция: {data_player.role}'
                                     f'\nВаш трансферный статус: {data_player.transfer_status}',
                                     reply_markup=kb.player_kb)

# Отображает все клубы в виде Inline кнопок
@router.callback_query(F.data == "check_all_club")
async def handle_check_all_club(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(f'Выберите необходимый клуб',
                                        reply_markup=await kb.clubs())

# Показывает всех игроков в данном клубе
@router.callback_query(F.data.startswith('club_'))
async def handle_check_current_club(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(f'Игроки, играющие в этом клубе:',
                                            reply_markup= await kb.players(int(callback.data.split('_')[1])))
                                            # В функцию передается раделенный коллбек, из которого извлекается айди клуба




