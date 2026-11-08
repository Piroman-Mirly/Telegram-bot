import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware

# Импорты из реквестов
from app.database.all_requests import clubs as r_clubs
from app.database.all_requests import players as r_players
from app.database.all_requests import matches as r_matches

import app.keyboards.keyboards as user_kb
from app.states import Admin, Registration

router = Router()





# Комманда старт
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Admin.normal)

    data_player = await r_players.get_statistic_current_player(message.from_user.id)

    # Если вернули None, то значит такого пользователя нет и начинается регистрация
    if not data_player:
        await message.answer('Новый пользователь! Давайте зарегестрируемся.\nВведите ваш игровой ник')
        await state.set_state(Registration.nickname)
        return


    # В будущем переделать на один запрос с JOIN
    club_name = await r_clubs.get_club_name(data_player.club_id)
    text = (f'👤 <b>Профиль игрока</b>\n'
            f'━━━━━━━━━━━━━━━\n'
            f'<blockquote>'
            f'Никнейм: {data_player.nickname_player}\n'
            f'Клуб: {'👕 ' + club_name if data_player.club else "🏳️ Нет клуба"}\n'
            f'Ваша позиция: 🛡 {data_player.role}\n'
            f'Ваш трансферный статус: {data_player.transfer_status}'
            f'</blockquote>')


    await message.answer(text, reply_markup=user_kb.player_kb, parse_mode="HTML")
    

# Удаляет все сообщения, написанные в боте
@router.message(Admin.normal)
async def delete_all_message(message: Message, state: FSMContext):
    await message.delete()

# Коллбек, который отображает главное меню игрока / его профиль
@router.callback_query(F.data == "return_to_player_mm", StateFilter(Admin.normal))
async def handle_return_to_player_mm(callback : CallbackQuery):
    await callback.answer()
    data_player = await r_players.get_statistic_current_player(callback.from_user.id)
    # В будущем переделать на один запрос с JOIN
    club_name = await r_clubs.get_club_name(data_player.club_id)
    # Записываем текст в отдельную переменную, а потом уже используем её вместе со всеми парсерами типа HTML
    text = (f'👤 <b>Профиль игрока</b>\n'
            f'━━━━━━━━━━━━━━━\n'
            f'<blockquote>'
            f'Никнейм: {data_player.nickname_player}\n'
            f'Клуб: {'👕 ' + club_name if data_player.club else "🏳️ Нет клуба"}\n'
            f'Ваша позиция: 🛡 {data_player.role}\n'
            f'Ваш трансферный статус: {data_player.transfer_status}'
            f'</blockquote>')


    await callback.message.edit_text(text, reply_markup=user_kb.player_kb, parse_mode="HTML")
    
    