from app.database.models import async_session
from app.database.models import Player, Club, Coach, Statistic_per_match, Match, User
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date

from sqlalchemy import select, update, delete, func, desc


# Функция отвечает за добавление нового игрока
async def create_player(tg_id: int, nickname: str, role: str): 
    async with async_session() as session:
        player = Player(telegram_id=tg_id, nickname_player=nickname, role=role)
        session.add(player)
        # Попытка записать. Если ошибка, то гг :(
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def create_new_match(date: datetime, left_id: int, right_id: int):
    async with async_session() as session:
        match = Match(date_match=date, left_club_id=left_id, right_club_id=right_id)
        session.add(match)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()

async def get_all_clubs(): # Функция передает данные всех клубов
    async with async_session() as session:
        return (await session.scalars(select(Club))).all()

async def get_name_club(club_id): # Функция возвращает название конкретного клуба
    async with async_session() as session:
        return await session.scalar(select(Club.name_club).where(Club.id == club_id))


# Функция получает на вход айди клуба и сравнивает его со всеми игроками, после чего возвращает всех найденных игроков клуба
async def get_all_players_in_club(club_id):
    async with async_session() as session:
        players = await session.scalars(select(Player).where(Player.club_id == club_id))
        return players

# Функция получает на вход телеграмм айди игрока, а возвращает его обычное айди
async def get_player_id(telegram_id):
    async with async_session() as session:
        player_id = await session.scalar(select(Player.id).where(Player.telegram_id == telegram_id))
        return player_id

# Функция передает все данные конкретного игрока игрока с помощью полученного тг-айди
async def get_statistic_current_player(tg_id):
    async with async_session() as session:
        all_data_current_player = await session.scalar(select(Player).where(Player.telegram_id == tg_id))

        return all_data_current_player

# Функция возвращает название клуба
async def get_club_name(club_id):
    async with async_session() as session:
        club_name = await session.scalar(select(Club.name_club).where(Club.id == club_id))
        return club_name

# Функция возвращает отсортированную по очкам таблицу с клубами
async def get_data_for_table_clubs():
    async with async_session() as session:
        # Создаю промежуточную таблицу в формате id_клуба - кол-во побед
        wins_table = (
            select(Match.winner_id.label("club_id"), func.count(Match.id).label("wins"))
            .group_by(Match.winner_id).subquery()
                      )
        # Делаю основной запрос, используя ту промежуточную таблицу, создав объединенную таблицу из прошлой.

        # coalesce принимает в качестве аргумента Х и У. Если Х = Null, то выведет У
        # Если X != Null, то выведет Х
        # Из первой таблицы берётся кол-во побед и умножается на 3 ,если они есть, и возвращается 0, если их нет
        query = (select(Club.id, Club.name_club, (func.coalesce(wins_table.c.wins, 0) * 3).label("points"),
                        func.coalesce(wins_table.c.wins, 0).label("wins"),
                        ).outerjoin(wins_table, Club.id == wins_table.c.club_id)
                        .order_by(desc("points"), desc("wins")) # Сортировка от большего к меньшему сначала по очкам, а потом по победам.
                        )

        # Вернёт таблицу в формате: id, name_club, wins, points
        result = await session.execute(query)
        return result.all()

# Функция возвращает суммарную статистику игрока
async def get_all_points_player(player_id):
    async with async_session() as session:
        # Промежуточный массив, который будет содержать в себе 3 значения: сумма атаки, блока и подач
        all_point_array = []
        # Используем айди игрока, чтобы получить данные о всех его матчах
        sum_attack = select(func.sum(Statistic_per_match.attack_per_match)).where(Statistic_per_match.player_id == player_id)
        all_point_array.append((await session.execute(sum_attack)).scalar())
        # Очки за блок
        sum_block = select(func.sum(Statistic_per_match.block_per_match)).where(Statistic_per_match.player_id == player_id)
        all_point_array.append((await session.execute(sum_block)).scalar())
        # Очки за подачу
        sum_serve = select(func.sum(Statistic_per_match.serve_per_match)).where(Statistic_per_match.player_id == player_id)
        # Массив со всей суммой очков
        all_point_array.append((await session.execute(sum_serve)).scalar())
        return all_point_array

# Функция возвращает все матчи
async def get_all_matches():
    async with async_session() as session:
        result = await session.scalars(select(Match))
        return result.all()

# Функция возвращает кортеж из двух клубов
async def get_two_club_id_in_match(match_id):
    async with async_session() as session:
        # Айди извлекаются напрямую из нужного матча
        left_id = await session.scalar(select(Match.left_club_id).where(Match.id == match_id))
        right_id = await session.scalar(select(Match.right_club_id).where(Match.id == match_id))

        left_club = await session.get(Club, left_id)
        right_club = await session.get(Club, right_id)

        pair = (left_club, right_club)
        return pair

# Функция возвращает топ-10 по указанным категориям
# Всего категорий может быть 4: атака, блок, подача и всего очков
async def get_top_players(category: str = 'total', limit: int = 10):
    async with async_session() as session:
        total_points = (
            func.coalesce(func.sum(Statistic_per_match.attack_per_match), 0) +
            func.coalesce(func.sum(Statistic_per_match.block_per_match), 0) +
            func.coalesce(func.sum(Statistic_per_match.serve_per_match), 0)
        )

        query = (
            select(Player.nickname_player, Club.name_club,
                   func.coalesce(func.sum(Statistic_per_match.attack_per_match), 0).label("attack"),
                   func.coalesce(func.sum(Statistic_per_match.block_per_match), 0).label("block"),
                   func.coalesce(func.sum(Statistic_per_match.serve_per_match), 0).label("serve"),
                   total_points.label("total_points")
                   )
                    # Соединяем таблицу клубов (Player.club_id == Club.id)
                    .join(Club, Player.club_id == Club.id)
                    .outerjoin(Statistic_per_match, Player.id == Statistic_per_match.player_id)
                    .group_by(Player.id, Player.nickname_player, Club.name_club)
                    .order_by(desc("total_points"))
        )

        # Выбор, по какой колонке сортировать
        order_map = {
            "attack": desc("attack"),
            "block": desc("block"),
            "serve": desc("serve"),
            "total": desc("total_points")
        }

        # order_map.get(category, desc("total_points")) защищает от опечаток
        # если передашь неизвестную категорию, сортировка будет по общим очкам.
        query = query.order_by(order_map.get(category, desc("total_points")))

        result = await session.execute(query)
        return result.all() # Список кортежей в формате: [(ник, клуб, атака, блок, подача, всего очков)]


# Возвращает матчи конкретного дня
async def get_target_date_matches(target_date: date):
    async with async_session() as session:
        query = (
            select(Match).where(Match.date_match == target_date)
            .order_by(Match.id) # Сортировка по времени создания
        )
        result = await session.scalars(query)
        return result.all()