from app.database.models import async_session
from app.database.models import Player, Club, Coach, Statistic_per_match, Match, User

from sqlalchemy import select, update, delete

async def set_user(tg_id: int, username_db: str): # Функция отвечает за добавление нового пользователя
    async with async_session() as session:
        # В переменную user передается объект пользователя из БД с подходящим именем и тг айди
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))

        # Если такого пользователя нет, то он создается
        if not user:
            session.add(User(telegram_id = tg_id, username = username_db))
            await session.commit()


async def get_all_clubs(): # Функция передает данные всех клубов
    async with async_session() as session:
        return await session.scalars(select(Club))


# Функция получает на вход айди клуба и сравнивает его со всеми игроками, после чего возвращает всех найденных игроков клуба
async def get_all_players_in_club(club_id):
    async with async_session() as session:
        players = await session.scalars(select(Player).where(Player.club_id == club_id))
        return players


# Функция передает все данные конкретного игрока игрока с помощью полученного тг-айди
async def get_statistic_current_player(tg_id):
    async with async_session() as session:
        all_data_current_player = await session.scalar(select(Player).where(Player.telegram_id == tg_id))

        return all_data_current_player
