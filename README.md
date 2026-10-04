# Telegram-bot
This is my first bot project. This bot will help you deal with the routine tasks of running a virtual esports league
Это мой первый проект — ТГ-бот. Этот бот должен помогать решать рутинные задачи во время ведения виртуальной киберспортивной лиги.


Если подробнее, то на просторах Steam есть различного рода онлайн-игры про спорт, такие как серия игр FIFA.

Но если с фифой всё понятно, — в ней есть свой киберспорт с огромными призовыми турнирами, своя лига внутри игры и огромное сообщество, — то с другими, малоизвестными играми, всё куда сложнее.
Есть игра под названием PUCK. Её смысл прост: ты играешь в хоккей от первого лица против таких же ТикТок монстров как и ты. 
В ней присутствует набор базовых функций для низкобюджетного проекта: сложная механика ведения шайбы, матчи с тремя периодами по пять минут и даже возможность выбрать позицию на поле.
И на этом плюсы этой игры заканчиваются. Да, недавно в ней вышло обновление с добавлением рейтингового режима, но, откровенно говоря, эта игра довольно-таки скучна.
При этом она до сих пор популярна. Всё из-за сообщества это игры, которые используют формат песочницы как душе угодно. 
Они организуют товарищеские шоу-матчи, клипают нарезки в ТикТок и даже создают свои собственные лиги.

И именно ради последнего я и захотел создать этого бота. В основном энтузиасты, которые создают такие лиги на 200-300 подписчиков, страдают от нехватки кадров.
Лига нуждается в постоянной поддержке, и если дизайнера и можно как-то заменить с помощью ИИ, то заменить человека, который будет следить за статистикой, будет тяжело.

MVP моего бота будет иметь базовый набор функций для использования. О них вы можете почитать ниже. Я постараюсь сделать этот проект таким, чтобы его можно было использовать в реальных задачах.
В качестве эксперимента я создам свою лигу, но уже в другой игре — VolleyHub, которая, на данный момент, находится в открытом бетта-тесте. 

To be more specific, there are various online sports games on Steam, such as the FIFA series.

But while everything is clear with FIFA — it has its own esports scene with huge prize tournaments, its own league within the game, and a huge community — things are much more complicated with other, lesser‑known games.
There’s a game called PUCK. The idea is simple: you play first‑person hockey against TikTok monsters just like you. 
It includes a set of basic features for a low‑budget project: a complex puck‑handling mechanic, matches with three five‑minute periods, and even the ability to choose a position on the field.
And that’s where the game’s advantages end. Yes, it recently received an update that added a ranked mode, but, frankly speaking, this game is rather boring.
At the same time, it’s still popular. It’s all because of the community — these are games that use the sandbox format to their heart’s content. 
They organize friendly show matches, post clips on TikTok, and even create their own leagues.

And it’s precisely for the latter that I wanted to create this bot. Mostly, enthusiasts who create such leagues with 200–300 subscribers suffer from a lack of personnel.
The league needs constant support, and while a designer can somehow be replaced with the help of AI, it will be hard to replace the person who will monitor the statistics.

The MVP of my bot will have a basic set of functions for use. You can read about them below. I will try to make this project so that it can be used in real‑world tasks.
As an experiment, I will create my own league, but this time in another game — VolleyHub, which is currently in open beta testing.


I tried to create a small logical diagram for the MVP of my bot, and here it is:
Я постарался сделать небольшую логическую диаграмму для MVP моего бота, вот она:


<img width="980" height="642" alt="Бот ТГ jpeg" src="https://github.com/user-attachments/assets/9d014d46-60f3-4912-ae00-aff529288107" />

Итак, что касается функций. Вот, что я планирую сделать (или уже сделал):
1. Просмотр статистики игрока по единому шаблону в главном меню ✓
2. Возможность просмотреть все существующие клубы на данный момент ✓
3. Оформить страницу клуба по единому шаблону, которая будет содержать в себе: название клуба, кол-во игроков, место в таблице. ✗
4. Сделать работающие кнопки в профиле клуба: просмотр игроков всех игроков с возможностью посмотреть личную статистику каждого (пока только эта кнопка) ✗
5. Сделать работающую кнопку "Таблица", которая в реальном времени будет считать очки клубов и выстраивать их по убыванию, как в настоящей таблице ✗
6. Создать админ-панель, которая позволит судьям и админам удобно заполнять протокол матча (кто сколько забил и тд.) с возможностью исправить свою ошибку. ✗

Планы на будущее:
1. Сделать трансферный рынок — У меня уже есть колонка "transfer_status" в таблице "players" моей БД. Теперь нужно создать отдельное окно трансферного рынка с пагинацией и возможностью сортировать игроков по трансферному статусу и роли.
2. Возможность вести детальный счёт статистики + детальный просмотр матча — Админ-панель в моих планах выполняет простенькие задачи: записать кол-во очков конкретного игрока за матч и сохранить эти данные в БД. Однако, если я хочу, чтобы статистика матча выглядела красиво, то, как минимум, ко всему этому нужно добавить счёт очков по отдельным партиям.
   
