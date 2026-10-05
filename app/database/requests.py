from app.database.models import async_session
from app.database.models import Player, Club, Coach, Statistic_per_match, Match, User

from sqlalchemy import select, update, delete, func, desc

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
async def get_all_points_player(tg_id):
    async with async_session() as session:
        # Промежуточный массив, который будет содержать в себе 3 значения: сумма атаки, блока и подач
        all_point_array = []
        # Получаем айди игрока с помощью тг айди
        id_player = await session.scalar(select(Player.id).where(Player.telegram_id == tg_id))
        # Используем айди игрока, чтобы получить данные о всех его матчах
        sum_attack = select(func.sum(Statistic_per_match.attack_per_match)).where(Statistic_per_match.player_id == id_player)
        all_point_array.append((await session.execute(sum_attack)).scalar())
        # Очки за блок
        sum_block = select(func.sum(Statistic_per_match.block_per_match)).where(Statistic_per_match.player_id == id_player)
        all_point_array.append((await session.execute(sum_block)).scalar())
        # Очки за подачу
        sum_serve = select(func.sum(Statistic_per_match.serve_per_match)).where(Statistic_per_match.player_id == id_player)
        # Массив со всей суммой очков
        all_point_array.append((await session.execute(sum_serve)).scalar())
        return all_point_array
    