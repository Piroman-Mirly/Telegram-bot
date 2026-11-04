from app.database.models import async_session
from app.database.models import Match
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from sqlalchemy import select, update

# Создает новый матч в БД
async def create_new_match(date: datetime, left_id: int, right_id: int):
    async with async_session() as session:
        match = Match(date_match=date, left_club_id=left_id, right_club_id=right_id)
        session.add(match)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()

# Обновляет существующий матч в БД
async def update_match_score(match_id: int, score_left: int, score_right: int, winner_id: int):
    async with async_session() as session:
        query = (update(Match).where(Match.id == match_id)
                 .values(score_left = score_left,
                         score_right = score_right,
                         winner_id = winner_id,
                         status = 'finished'))
        await session.execute(query)
        await session.commit()