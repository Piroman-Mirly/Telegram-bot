from aiogram.fsm.state import StatesGroup, State


# FSM состояния админ-панели
class Admin(StatesGroup): 



    # Статус, чтобы удалять весь мусор в сообщениях
    normal = State()
    # Общие статусы
    make_choice = State() # Делает выбор команды перед заходом в админку

    # Статусы для главного админа, доступ к которым даётся конкретному тг-айди
    add_left_club = State() # Добавил первый клуб в матче
    add_right_club = State() # Добавил второй клуб в матче
    add_date = State() # Добавил дату матча

    # Статусы для обычного судьи
    picking_match = State() # Судья выбрал матч
    picking_club = State() # Судья выбрал клуб
    picking_player = State() # Судья выбрал конкретного игрока
    entering_stats = State() # Судья ввёл значения статистики конкретному игроку
    confirming_match = State() # Судья подтвердил значения

 # Состояния для регистрации
class Registration(StatesGroup):
    # Бот ждёт имя
    nickname = State()
    
    # Бот ждёт позицию
    await_role = State()

    # Подвтерждение регистрации
    confirm_reg = State()