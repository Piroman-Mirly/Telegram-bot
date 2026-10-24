import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.middlewares import TestMiddleware
import app.database.requests as request

import app.keyboards.keyboards as user_kb
from app.states import Admin

router = Router()




# Колбек, который переносит пользователя в окно выбора категории для показа статистики топ-10
@router.callback_query(F.data == 'choice_category_statistic', StateFilter(Admin.normal))
async def handle_make_choice_category_statistic_top_10_players(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Выберите категорию статистики', reply_markup=user_kb.filter_category)



# Колбек отвечает за вывод статистики всех игроков
@router.callback_query(F.data.startswith("top_"), StateFilter(Admin.normal))
async def handle_top_players_statistic(callback: CallbackQuery):
    await callback.answer()

    # Из callback'а достаём категорию: "top_attack" → "attack"
    category = callback.data.split("_")[1]

    # Список кортежей в формате: [(ник, клуб, атака, блок, подача, всего очков)] с лимитом в 10 игроков
    top = await request.get_top_players(category=category, limit=10)

    # Переводим в человекочитаемый заголовок
    titles = {
        "attack": "⚔️ Топ-10 по атаке",
        "block":  "🧱 Топ-10 по блоку",
        "serve":  "🎾 Топ-10 по подаче",
        "total":  "🏆 Топ-10 по общим очкам",
    }
    # Если нет статистики, то бот предупредит
    if not top:
        await callback.message.edit_text("Статистики пока нет.", reply_markup=user_kb.return_to_mm)
        return

    # Создается текст для вывода топ-10
    lines = [f"<b>{titles.get(category, 'Топ-10')}</b>\n"]


    # Цикл, который создает топ-10 игроков по ка тегории
    for place, row in enumerate(top, start=1):
        nickname, club_name, attack, block, serve, total = row

        # Значение, по которому сортируем, — подсветим жирным
        values = {"attack": attack, "block": block, "serve": serve, "total": total}
        highlight = values.get(category, total)

        lines.append(
            f"{place}. <b>{nickname}</b> ({club_name}) — <b>{highlight}</b>\n"
            f"   ⚔️ {attack} | 🧱 {block} | 🎾 {serve} | 🏆 {total}"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=user_kb.return_to_category_statisitc,
        parse_mode="HTML",
    )

