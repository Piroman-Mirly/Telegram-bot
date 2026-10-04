from sqlalchemy import BigInteger, String, ForeignKey, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from datetime import date 

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Таблица со всеми игроками
class Player(Base):
    __tablename__ = 'players' # Название таблицы, содержащей всех игроков

    id: Mapped[int] = mapped_column(primary_key=True) # Персональный айди всех игроков

    telegram_id: Mapped[int] = mapped_column(BigInteger) # Телеграм айди игрока
    nickname_player: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Игровой ник
    role: Mapped[str] = mapped_column(String(25), nullable=False) # Позиция на поле
    transfer_status: Mapped[str] = mapped_column(String(32), nullable=False) # Трансферный статус
    club_id: Mapped[int] = mapped_column(ForeignKey('clubs.id')) # Внешний ключ от клуба

    club: Mapped["Club"] = relationship( back_populates='players', lazy='selectin') # Связь игрока с клубом

# Таблица со всеми клубами
class Club(Base):
    __tablename__ = 'clubs' # Название таблицы, содержащей все клубы

    id: Mapped[int] = mapped_column(primary_key=True) # Персональный айди всех клубов

    name_club: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Название клуба
    coach_id: Mapped[int] = mapped_column(ForeignKey('coaches.id')) # Внешний ключ от тренера

    players: Mapped[list["Player"]] = relationship(
        back_populates='club', lazy='selectin') # Связь клуба с игроком

# Таблица со всеми тренерами
class Coach(Base):
    __tablename__ = 'coaches' # Название таблицы, содержащей всех тренеров

    id: Mapped[int] = mapped_column(primary_key=True) # Персональный айди всех тренеров

    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False) # Телеграм айди тренера

    nickname_coach: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Игровой ник тренера

# Таблица со всей статистикой в матче
class Statistic_per_match(Base):
    # Название таблицы, содержащей статистику всех игроков в матче
    __tablename__ = 'Statistics_players_per_match' 
    
    id: Mapped[int] = mapped_column(primary_key=True) # Персональный айди статистики

    attack_per_match: Mapped[int] = mapped_column(nullable=False) # Количество очков с атаки
    block_per_match: Mapped[int] = mapped_column(nullable=False) # Количество очков с блока
    serve_per_match: Mapped[int] = mapped_column(nullable=False) # Количество очков с подачи

    player_id: Mapped[int] = mapped_column(ForeignKey('players.id')) # Айди игрока
    match_id: Mapped[int] = mapped_column(ForeignKey('matches.id')) # Айди матча

# Таблица со всеми матчами
class Match(Base):
    __tablename__ = 'matches' # Название таблицы, содержащей все матчи

    id: Mapped[int] = mapped_column(primary_key=True) # Персональный айди всех матчей

    date_match: Mapped[date] = mapped_column(Date, nullable=False)  # Дата матча
    winner_id: Mapped[int] = mapped_column(ForeignKey('clubs.id')) # Айди победителя в матче

    left_club_id: Mapped[int] = mapped_column(ForeignKey('clubs.id')) # Айди клуба дома
    right_club_id: Mapped[int] = mapped_column(ForeignKey('clubs.id')) # Айди клуба на выезде

    score_left: Mapped[int] = mapped_column(nullable=False) # Счёт по партиям левого клуба
    score_right: Mapped[int] = mapped_column(nullable=False) # Счёт по партиям правого клуба


# Класс тех, кто хоть раз зашёл в бота и нажал кнопку старта
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False) # Как юсер подписан в тг

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)