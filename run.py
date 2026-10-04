import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import TOKEN
from app.handlers import router

from app.database.models import async_main

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Бот бесконечно работает
async def main():
    await async_main()
    dp.include_router(router)
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