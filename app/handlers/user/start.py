import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError

from app.middlewares import TestMiddleware

from config import TG_ID_OWNER

# Импорты из реквестов
from app.database.all_requests import clubs as r_clubs
from app.database.all_requests import players as r_players
from app.database.all_requests import matches as r_matches

import app.keyboards.keyboards as user_kb
import app.keyboards.admin_kb as adm_kb
from app.states import Admin, Registration

router = Router()





# Комманда старт
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Admin.normal)
    
    tg_id = message.from_user.id
    username = message.from_user.username
    # Смотрим, есть ли такой пользователь вообще
    user = await r_players.get_user(message.from_user.id)
    # Если нет, то регистрируем
    if not user:
        await r_players.create_user(tg_id, username)
        await message.answer("Привет! Вы находитесь в гостевом режиме.", reply_markup=user_kb.appky_player_kb)
        return
    elif user.role == "guest": # Если он гость, то также выводим пользовательский интерфейс
        await message.answer("Привет! Вы находитесь в гостевом режиме.", reply_markup=user_kb.appky_player_kb)
        return
        

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
    

# Хендлер для отправки запроса на становление игрока
@router.callback_query(F.data == 'apply_for_player')
async def handle_apple(callback: CallbackQuery):
    await callback.answer()
    # Получаем самого пользователя
    user = await r_players.get_user(callback.from_user.id)
    
    # Проверка, не игрок ли пришедший человек игроком
    if user.role == 'player':
        await callback.message.edit_text('Вы уже являетесь игроком!')
        return
    
    # Формируем текст заявки для админа
    username = f"@{callback.from_user.username}" if callback.from_user.username else "нет username"
    text = (
        f"🔔 <b>Новая заявка на вступление!</b>\n\n"
        f"Имя: {callback.from_user.full_name}\n"
        f"Юзернейм: {username}\n"
        f"ID: <code>{callback.from_user.id}</code>\n\n"
        f"Одобрить пользователя?"
    )
    # Отправляем админу (мне)
    try:
        await callback.bot.send_message(
            chat_id=TG_ID_OWNER, # Сюда подставляется твой telegram_id из config.py
            text=text,
            reply_markup=adm_kb.application_kb(callback.from_user.id),
            parse_mode="HTML"
        )
        await callback.message.edit_text("✅ Заявка отправлена на рассмотрение администратору. Ожидайте ответа!")
    except TelegramForbiddenError:
        await callback.message.edit_text("❌ Ошибка: Администратор пока не может принимать заявки.")
    