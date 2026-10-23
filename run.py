import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import TOKEN
from app.handlers.user_handlers import router as main_router
from app.handlers.admin_handler import admin_router
from app.handlers.regist_handler import regist_router
from app.handlers.admin_add_statistic import admin_router as add_stat
from app.handlers.admin_create_match import admin_router as create_match

from app.database.models import async_main

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Бот бесконечно работает
async def main():
    await async_main()
    dp.include_router(add_stat)
    dp.include_router(create_match)
    dp.include_router(admin_router)
    dp.include_router(regist_router)
    dp.include_router(main_router)
    await dp.start_polling(bot)


# logging позваляет видеть расширенные данные в консоли. 
# При расширении проекта будет тратить много ресурсов бота, тормозя его.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Завершение работы')



# Добавил гит
# Теперь вроде всё отображается