from app.database.models import async_session
from app.database.models import Player, Club, Statistic_per_match, Match
#from sqlalchemy.exc import IntegrityError
#from datetime import datetime, date

from sqlalchemy import select, func, desc, or_, distinct, and_


# Извлекает имя игрока из БД с помощью его айди
async def get_nickname_player(player_id):
    async with async_session() as session:
        nickname = await session.scalar(select(Player.nickname_player).where(Player.id == player_id))
        return nickname

# Функция получает на вход айди клуба и возвращает всех найденных игроков этого клуба
async def get_all_players_in_club(club_id):
    async with async_session() as session:
        players = await session.scalars(select(Player).where(Player.club_id == club_id))
        return players

# Функция возвращает только тех игроков, у которых нет статистики
async def get_unifillied_players(club_id: int, match_id: int):
    async with async_session() as session:
        # Находим айди всех игроков, у которых уже есть статистика
        filled_player_subquery = (select(Statistic_per_match.player_id)
                                  .where(Statistic_per_match.match_id == match_id)
                                  )
        # Основной запрос
        query = (select(Player).where(Player.club_id == club_id)
                 .where(Player.id.not_in(filled_player_subquery)))
        result = await session.scalars(query)
        return result.all()

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

# Функция возвращает суммарную статистику игрока
async def get_all_points_player(player_id):
    async with async_session() as session:
        query = (select(
            func.coalesce(func.sum(Statistic_per_match.attack_per_match), 0).label("attack"),
            func.coalesce(func.sum(Statistic_per_match.block_per_match), 0).label("block"),
            func.coalesce(func.sum(Statistic_per_match.serve_per_match), 0).label("serve")
        ).join(Match, Statistic_per_match.match_id == Match.id)
        .where(Statistic_per_match.player_id == player_id)
        .where(Match.status == 'finished')
        )

        result = await session.execute(query)
        row = result.one()
        return row[0], row[1], row[2]

# Функция возвращает топ-10 по указанным категориям
# Всего категорий может быть 4: атака, блок, подача и всего очков
async def get_top_players(category: str = 'total', limit: int = 10):
    async with async_session() as session:
        total_points = (
            func.coalesce(func.sum(Statistic_per_match.attack_per_match), 0) +
            func.coalesce(func.sum(Statistic_per_match.block_per_match), 0) +
            func.coalesce(func.sum(Statistic_per_match.serve_per_match), 0)
        )

        # Подзапрос со списком ID завершенных матчей
        finished_matches_subq = select(Match.id).where(Match.status == 'finished')

        query = (
            select(Player.nickname_player, Club.name_club,
                   func.coalesce(func.sum(Statistic_per_match.attack_per_match), 0).label("attack"),
                   func.coalesce(func.sum(Statistic_per_match.block_per_match), 0).label("block"),
                   func.coalesce(func.sum(Statistic_per_match.serve_per_match), 0).label("serve"),
                   total_points.label("total_points")
                   )
                    # Соединяем таблицу клубов (Player.club_id == Club.id)
                    .join(Club, Player.club_id == Club.id)
                    # С помощью подзапроса считаем только статистику завершенных матчей
                    .outerjoin(
                        Statistic_per_match, 
                        and_(Player.id == Statistic_per_match.player_id,
                             Statistic_per_match.match_id.in_(finished_matches_subq)
                             )
                        )
                    .group_by(Player.id, Player.nickname_player, Club.name_club)
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
        query = query.limit(limit)

        result = await session.execute(query)
        return result.all() # Список кортежей в формате: [(ник, клуб, атака, блок, подача, всего очков)]

# Возвращает два значения: кол-во игроков с заполненной статистикой и общее кол-во игроков в матче
async def get_all_count_players(match_id):
    async with async_session() as session:
        # Узнаем данные матча
        match = await session.get(Match, match_id)

        if not match:
            return 0, 0

        # Общее кол-во игроков в клубе
        total_query = select(func.count(Player.id)).where(
            or_(
                Player.club_id == match.left_club_id,
                Player.club_id == match.right_club_id
            )
        )
        total_players = await session.scalar(total_query) or 0

        # Игроки с заполненной статистикой без дупликатов
        filled_query = select(
            func.count(func.distinct(Statistic_per_match.player_id))
        ).where(Statistic_per_match.match_id == match_id)

        filled_players = await session.scalar(filled_query) or 0

        return filled_players, total_players

