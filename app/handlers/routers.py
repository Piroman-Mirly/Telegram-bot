from aiogram import Router

# Файл со всеми роутерами

from app.handlers.admin.admin_add_statistic import admin_router as adm_add_statistic
from app.handlers.admin.admin_create_match import admin_router as adm_create_match
from app.handlers.admin.admin_handler import admin_router as main_admin

from app.handlers.user.check_statistic import router as check_statistic_router
from app.handlers.user.regist_handler import regist_router as regist_router
from app.handlers.user.schedule import router as schedule_router
from app.handlers.user.start import router as start_router
from app.handlers.user.table import router as table_router
from app.handlers.user.top_10 import router as top_10_router

# Создаем главные роутеры
user_router = Router(name='user')
admin_router = Router(name='admin')


# Подключаем к главным роутерам дочерние
# Роутеры пользователя
user_router.include_router(start_router)
user_router.include_router(regist_router)
user_router.include_router(check_statistic_router)
user_router.include_router(table_router)
user_router.include_router(top_10_router)
user_router.include_router(schedule_router)

# Роутеры админа
admin_router.include_router(main_admin)
admin_router.include_router(adm_create_match)
admin_router.include_router(adm_add_statistic)
