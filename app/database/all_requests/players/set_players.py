from app.database.models import async_session
from app.database.models import Player, Statistic_per_match
from sqlalchemy.exc import IntegrityError
#from datetime import datetime, date

from sqlalchemy import select, update, delete, func, desc, or_

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

# Создает новую статистику игрока в БД
async def create_statistic_player(attack: int, block: int, serve: int, player_id: int, match_id: int):
    async with async_session() as session:
        statistic = Statistic_per_match(attack_per_match=attack,
                                        block_per_match=block,
                                        serve_per_match=serve,
                                        player_id=player_id,
                                        match_id=match_id)
        session.add(statistic)
        
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()  