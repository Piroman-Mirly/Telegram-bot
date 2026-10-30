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

    # Запоминает айди выбранного матча
    await state.update_data(match_id = int(callback.data.split('_')[-1]))

    # Кнопки клубов
    buttons = await adm_kb.clubs(clubs) # Клубы передаются в билдер кнопок


    await callback.message.edit_text('Выберите клуб, статистику игроков которых вы желаете внести:', reply_markup=buttons)


# Показывает всех игроков в данном клубе
@admin_router.callback_query(F.data.startswith('club_'), StateFilter(Admin.picking_club)) # Сработает только в состоянии normal
async def handle_select_current_player(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    club_id = int(callback.data.split('_')[-1])

    data = await state.get_data()

    match_id = int(data.get('match_id'))

    # Сохраняет данные клуба
    await state.update_data(club_id = club_id)

    # Делаем запрос в БД, чтобы поместь в переменную игроков без статистики
    unfilled_players = await request.get_unifillied_players(club_id, match_id)

     # ВАЖНО: Проверяем, остались ли вообще игроки для заполнения
    if not unfilled_players:
        await callback.message.edit_text(
            'Все игроки этого клуба уже имеют статистику за этот матч!\n'
            'Вы можете вернуться назад и выбрать другой клуб',
            reply_markup=adm_kb.back_to_clubs # Кнопка возврата
        )
        return

    buttons = await adm_kb.list_players(unfilled_players)
    
    await callback.message.edit_text(f'Выберите игрока, статистику которого вы хотите добавить / изменить:',
                                            reply_markup=buttons)
                                            # В функцию передается разделенный коллбек, из которого извлекается айди клуба
    await state.set_state(Admin.picking_player)

# Просит вписать данные игрока
@admin_router.callback_query(F.data.startswith('player_'), StateFilter(Admin.picking_player))
async def handle_add_statistic_player(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    player_id = int(callback.data.split('_')[-1])
    
    # Запоминает айди игрока, которому необходимо записать статистику
    await state.update_data(player_id = player_id)
    

    await callback.message.edit_text('Введите статистику игрока за матч в формате:\n' \
    'Атака, блок, подача', reply_markup=adm_kb.back_to_players)

    await state.set_state(Admin.entering_stats)

# Предварительный этап перед подтверждением данных
@admin_router.message(Admin.entering_stats)
async def handle_entering_statistic_player(message: Message, state: FSMContext):
    # Получаем статистику от судьи
    all_statistic = message.text.strip()

    # Извлекаем айди игрока
    data = await state.get_data()
    player_id = data.get('player_id')

    # Узнаем имя игрока
    nickname_player = await request.get_nickname_player(player_id)

    # Убираем все лишние пробелы и разбиваем по запятой (работает и для "3,5,0", и для "3, 5, 0")
    cleaned_text = all_statistic.replace(" ", "")
    parts = cleaned_text.split(',')

    # Проверяем, что введено ровно 3 значения
    if len(parts) != 3:
        await message.answer(
            'Ошибка! Вы ввели не 3 значения.\n'
            'Пожалуйста, введите данные по шаблону: Атака, Блок, Подача\n'
            'Например: 3, 5, 0',
            reply_markup=adm_kb.back_to_players # Кнопка "Назад к выбору игрока"
        )
        return

    # Пытаемся конвертировать строки в целые числа
    try:
        attack = int(parts[0])
        block = int(parts[1])
        serve = int(parts[2])

        # Дополнительная проверка: очки не могут быть отрицательными
        if attack < 0 or block < 0 or serve < 0:
            raise ValueError("Отрицательные числа")
            
    except ValueError:
        await message.answer(
            'Ошибка! Вы ввели не числа или отрицательные числа.\n'
            'Пожалуйста, введите данные по шаблону: 3, 5, 0',
            reply_markup=adm_kb.back_to_players
        )
        return

    # Все проверки пройдены, данные корректны. Записываем в FSM.
    await state.update_data(attack=attack, block=block, serve=serve)

    await message.answer(
        f'Проверьте данные\n'
        f'Игрок: {nickname_player}\n'
        f'Очки за атаку: {attack}\n'
        f'Очки за блок: {block}\n'
        f'Очки за подачу: {serve}\n', 
        reply_markup=adm_kb.succses_statistic
    )

    # Смена состояния на подтверждение
    await state.set_state(Admin.confirming_stats)


# Подтверждение статистики игрока и занесение её в БД
@admin_router.callback_query(F.data == 'succses_statistic', StateFilter(Admin.confirming_stats))
async def handle_confirm_stats(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    # Данные заносятс в БД
    data = await state.get_data()
    player_id = data.get('player_id')
    match_id = data.get('match_id')

    attack = data.get('attack')
    block = data.get('block')
    serve = data.get('serve')

    await request.create_statistic_player(attack, block, serve, player_id, match_id)

    await callback.message.edit_text('Данные успешно занесены в базу данных', reply_markup=adm_kb.back_to_matches)

