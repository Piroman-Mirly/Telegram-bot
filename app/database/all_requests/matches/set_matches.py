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
                         winner_id = winner_id))
        await session.execute(query)
        await session.commit()

async def update_status_match(match_id: int):
    async with async_session() as session:
        # Смотрим, какой сейчас статус матча
        current_status = await session.scalar(select(Match.status).where(Match.id == match_id))

        # Меняем статус на противоположный
        if current_status == 'finished':
            status_to_switch = 'scheduled'
        elif current_status == 'scheduled':
            status_to_switch = 'finished'

        query = (update(Match).where(Match.id == match_id)
                 .values(status = status_to_switch))
        await session.execute(query)
        await session.commit()
        
