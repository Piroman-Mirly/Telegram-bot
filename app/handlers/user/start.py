import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware
import app.database.requests as request

import app.keyboards.keyboards as user_kb
from app.states import Admin, Registration

router = Router()





# Комманда старт
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Admin.normal)

    data_player = await request.get_statistic_current_player(message.from_user.id)

    # Если вернули None, то значит такого пользователя нет и начинается регистрация
    if not data_player:
        await message.answer('Новый пользователь! Давайте зарегестрируемся.\nВведите ваш игровой ник')
        await state.set_state(Registration.nickname)
        return


    # В будущем переделать на один запрос с JOIN
    club_name = await request.get_club_name(data_player.club_id)
    await message.answer(f'———Главный экран———'
                                     f'\nВаш игровой ник: {data_player.nickname_player}'
                                     f'\nНазвание клуба: {club_name}'
                                     f'\nВаша позиция: {data_player.role}'
                                     f'\nВаш трансферный статус: {data_player.transfer_status}',
                                     reply_markup=user_kb.player_kb)
    

# Удаляет все сообщения, написанные в боте
@router.message(Admin.normal)
async def delete_all_message(message: Message, state: FSMContext):
    await message.delete()

# Коллбек, который отображает главное меню игрока / его профиль
@router.callback_query(F.data == "return_to_player_mm", StateFilter(Admin.normal))
async def handle_return_to_player_mm(callback : CallbackQuery):
    await callback.answer()
    data_player = await request.get_statistic_current_player(callback.from_user.id)
    # В будущем переделать на один запрос с JOIN
    club_name = await request.get_club_name(data_player.club_id)
    # Меняет последний текст бота на статистику игрока.
    await callback.message.edit_text(f'———Главный экран———'
                                     f'\nВаш игровой ник: {data_player.nickname_player}'
                                     f'\nНазвание клуба: {club_name}'
                                     f'\nВаша позиция: {data_player.role}'
                                     f'\nВаш трансферный статус: {data_player.transfer_status}',
                                     reply_markup=user_kb.player_kb)
    
    