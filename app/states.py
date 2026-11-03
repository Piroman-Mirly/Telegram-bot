from aiogram.fsm.state import StatesGroup, State


# FSM состояния админ-панели
class Admin(StatesGroup): 



    # Статус, чтобы удалять весь мусор в сообщениях
    normal = State()
    # Общие статусы
    make_choice = State() # Делает выбор команды перед заходом в админку

    # Статусы для создания матча
    set_date = State() # Пользователь устанавливает дату
    choice_left_club = State() # Выбирает первый клуб
    choice_right_club = State() # Выбирает второй клуб

    # Статусы для записи статистики в конкретный матч
    picking_match = State() # Судья выбрал матч
    picking_club = State() # Судья выбрал клуб
    picking_player = State() # Судья выбрал конкретного игрока
    entering_stats = State() # Судья вводит значения выбранному игроку
    confirming_stats = State() # Судья подтвердил значения

    # Запись счёта
    picking_match_for_score = State() #Судья добавляет счёт клубам
    confirming_score = State()

 # Состояния для регистрации
class Registration(StatesGroup):
    # Бот ждёт имя
    nickname = State()
    
    # Бот ждёт позицию
    await_role = State()

    # Подвтерждение регистрации
    confirm_reg = State()