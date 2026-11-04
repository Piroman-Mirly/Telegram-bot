from app.database.models import async_session
from app.database.models import Match
#from sqlalchemy.exc import IntegrityError
from datetime import date

from sqlalchemy import select, or_

# Возвращает матчи, которые имеют незаполненный статус "scheduled"
async def schedule_matches():
    async with async_session() as session:
        matches = await session.scalars(select(Match).where(Match.status == 'scheduled'))
        return matches.all()

# Возвращает матчи, счёт партий которых ещё незаполнен
async def none_score_matches():
    async with async_session() as session:
        matches = await session.scalars(select(Match).where(or_(Match.score_left == None, Match.score_right == None)))
        return matches.all()

# Возвращает конкретный матч по id
async def get_match_by_id(match_id):
    async with async_session() as session:
        query = await session.scalar(select(Match).where(Match.id == match_id))
        return query

# Функция возвращает все матчи
async def get_all_matches():
    async with async_session() as session:
        result = await session.scalars(select(Match))
        return result.all()

# Возвращает матчи конкретного дня
async def get_target_date_matches(target_date: date):
    async with async_session() as session:
        query = (
            select(Match).where(Match.date_match == target_date)
            .order_by(Match.id) # Сортировка по времени создания
        )
        result = await session.scalars(query)
        return result.all()
