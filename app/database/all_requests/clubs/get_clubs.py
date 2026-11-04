from app.database.models import async_session
from app.database.models import Player, Club, Coach, Statistic_per_match, Match, User
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date

from sqlalchemy import select, update, delete, func, desc, or_

# Функция передает данные всех клубов
async def get_all_clubs(): 
    async with async_session() as session:
        return (await session.scalars(select(Club))).all()

# Функция возвращает название конкретного клуба
async def get_name_club(club_id): 
    async with async_session() as session:
        return await session.scalar(select(Club.name_club).where(Club.id == club_id))

# Функции, которые возвращают левый и правые айди клубов
# Домашний клуб (левый)
async def get_left_club_id(match_id):
    async with async_session() as session:
        query = await session.scalar(select(Match.left_club_id).where(Match.id == match_id))

        return query

# Гостевой клуб (правый)
async def get_right_club_id(match_id):
    async with async_session() as session:
        query = await session.scalar(select(Match.right_club_id).where(Match.id == match_id))

        return query

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


