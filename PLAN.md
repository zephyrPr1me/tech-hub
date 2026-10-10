твоя задача в том что чтобы добавить зависимости и создать структуру проекта (без написания логики)

## План работ (этап: структура + зависимости)

Решения: **Poetry** (не uv) · дерево `backend/` из PLAN.md · пакета `techhub/` нет
(`package-mode = false`) · frontend пропускаем · зависимости — минимум · docker чиним.

1. **Реструктуризация файлов**
   - `main.py` → `backend/src/main.py`
   - `src/processor`, `src/scrapers` → `backend/src/…`, пустой `src/` удалить
   - `dockerfile` → `Dockerfile` (иначе `docker build .` не найдёт)

2. **Создать дерево по PLAN.md (всё пустое, только `__init__.py`)**
   ```
   backend/
   ├── alembic.ini            # заглушка-файл
   ├── alembic/versions/.gitkeep
   └── src/
       ├── main.py            # единственная «логика»: app = FastAPI()
       ├── config.py           # пустой стаб
       ├── api/{dependencies.py, v1/{router.py, endpoints/{news,tags,search}.py}}
       ├── core/{db.py, security.py}
       ├── scrapers/{telegram.py, rss.py, web.py}
       ├── processor/{deduplicator.py, scheduler.py}
       ├── ai/{client.py, prompts.py, schemas.py}
       ├── bot/{publisher.py, handlers/}
       └── models/, schemas/
   test/test_smoke.py
   README.md
   ```
   Alembic-скаффолдинг (`alembic init`) отложен: его нет в min-наборе зависимостей.

3. **pyproject.toml (Poetry 2.x, PEP 621)**
   - deps: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `pydantic-settings`, `httpx`
   - `[tool.poetry]`: `package-mode = false`, убрать `packages = [{include = "techhub"}]`
   - dev-группа: `pytest`, `pytest-asyncio`, `ruff`
   - pytest: `testpaths=["test"]`, `pythonpath=["backend/src"]`
   - `poetry lock && poetry install` → `poetry.lock`

4. **Docker**
   - Dockerfile: multi-stage `python:3.14-slim` + poetry → `poetry install --only main --no-root`
     → `CMD uvicorn --app-dir backend/src main:app --host 0.0.0.0 --port 8000`
   - docker-compose.yml: `{{...}}` → `${...}`, образ БД → `pgvector/pgvector:pg16`,
     сервис `app` (build `.`, port 8000, `depends_on: db`)
   - .env.example: `POSTGRES_USER/PASSWORD/DB`, `DATABASE_URL`; `.env` в `.gitignore`
   - проверить `.dockerignore` (не блокирует `backend/`, `poetry.lock`)

5. **Проверка**
   `poetry install` → `poetry run ruff check .` → `poetry run pytest`
   → `docker compose config -q` (+ `docker compose build`, если доступен docker)

> **Статус: выполнено.** `ruff check` — OK, `pytest` — 2 passed, `docker compose build`
> и полный `up` — OK (`/docs` → HTTP 200), расширение `vector` включено.
> Отклонения от плана: `ruff >=0.9` и `pytest-asyncio ^1.0` (версии из плана не
> поддерживали py314 / давали DeprecationWarning); контейнер БД переименован в
> `techhub_postgres`, хост-порт вынесен в `${POSTGRES_PORT:-5432}` (5432 занят
> контейнером проекта `url-shortner-v1`).

---

### Рекомендуемая структура проекта

```text
tech_hub_uz/
├── docker-compose.yml
├── pyproject.toml / uv.lock
├── README.md
│
├── backend/
│   ├── alembic/                      # Миграции базы данных
│   ├── alembic.ini
│   └── src/
│       ├── main.py                   # Точка входа (запуск FastAPI)
│       ├── config.py                 # Pydantic Settings (ENV переменные)
│       │
│       ├── api/                      # REST API для Frontend / Webhook'ов
│       │   ├── v1/
│       │   │   ├── endpoints/        # Роуты (news.py, tags.py, search.py)
│       │   │   └── router.py         # Главный роутер
│       │   └── dependencies.py       # DI (get_db_session, auth)
│       │
│       ├── core/                     # Ядро (подключение к БД, Redis, векторы)
│       │   ├── db.py                 # Async Engine и SessionMaker
│       │   └── security.py           # Авторизация / токены (если нужно)
│       │
│       ├── scrapers/                 # Модули парсинга и сбора
│       │   ├── telegram.py           # Telethon UserBot клиент
│       │   ├── rss.py                # Feedparser
│       │   └── web.py                # BeautifulSoup / Selectolax
│       │
│       ├── processor/                # Бизнес-логика обработки новостей
│       │   ├── deduplicator.py       # Поиск дубликатов через pgvector
│       │   └── scheduler.py          # APScheduler / фоновые задачи
│       │
│       ├── ai/                       # Интеграция с LLM
│       │   ├── client.py             # Вызовы OpenAI / Gemini
│       │   ├── prompts.py            # Промпты для классификации/суммаризации
│       │   └── schemas.py            # Pydantic-модели ответа от LLM (instructor)
│       │
│       ├── bot/                      # Telegram Bot (aiogram)
│       │   ├── handlers/             # Обработчики команд и сообщений
│       │   └── publisher.py          # Автопостинг дайджестов в канал
│       │
│       ├── models/                   # SQLAlchemy ORM Модели (News, Source, Tag)
│       └── schemas/                  # Pydantic схемы для API (Request/Response)
│
└── frontend/                         # Отдельное веб-приложение
    ├── public/
    └── src/                          # Компоненты, API-клиент, страницы

```

---

### Почему такое разделение будет работать идеально:

- **Модульность:** Каждый слой выполняет строго одну задачу. Если сменится LLM (например, переход с OpenAI на Gemini), меняется только папка `ai/`.

- **Единая БД:** И `bot`, и `api`, и `scrapers` используют общие модельки из `models/` и подключение из `core/db.py`.

- **Фоновый сбор:** `scrapers/` и `processor/` могут запускаться через планировщик (`scheduler.py`) прямо внутри приложения или отдельным воркером.

Разработка парсера и агрегатора IT/ИИ новостей Узбекистана разбивается на 5 основных слоев: **Сбор**, **Очереди/Планировщик**, **AI-обработка (LLM)**, **Хранение** и **Доставка/Интерфейс**.

Ниже оптимальный производственный стек, который обеспечит высокую скорость разработки и надежность системы.

СТЕК ТЕХНОЛОГИЙ

---

## 1. Сбор данных (Data Ingestion)

Поскольку основной объем узбекского IT-контента находится в Telegram, а остальное распределено по новостным порталам, нужны специализированные библиотеки:

- **Telethon** — асинхронные Python-клиенты для Telegram MTProto API (UserBot). Позволяют читать любые публичные каналы без ограничений стандатных ботов (`@itpark_uz`, `@spot_uz`, `@mitcuz`, IT-сообщества).
- **httpx** — современный асинхронный HTTP-клиент с поддержкой HTTP/2 (замена `requests`).
- **feedparser** — обработка RSS-лент (Spot.uz, Gazeta.uz, Daryo.uz, Курсив).
- **BeautifulSoup4** + **selectolax** — извлечение чистого текста из HTML-страниц (инструмент `selectolax` работает на C и парсит DOM значительно быстрее BeautifulSoup).

---

## 2. Планировщик и Очереди (Task Scheduling)

Для периодического опроса источников и фоновой обработки статей AI-моделью:

- **APScheduler** _(рекомендуемый старт)_ — если весь парсер работает в рамках одного асинхронного процесса. Прост в настройке, не требует сторонних сервисов.
- **ARQ** (на базе Redis) или **Celery** _(для масштабирования)_ — если нужно разделить процесс сбора и тяжелый процесс AI-обработки/суммаризации на разные воркеры.

---

## 3. Фильтрация, AI и Дедупликация (LLM & NLP)

Инструменты для классификации новостей, перевода и исключения дубликатов из разных источников:

- **OpenAI API (`gpt-4o-mini`)** или **Google Gemini 1.5 Flash** — высокоскоростные дешевые модели для:
- Оценки релевантности (отсев спама и рекламы).
- Извлечения тегов (`AI`, `Startups`, `Fintech`, `GovTech`, `Events`).
- Генерации коротких дайджестов (TL;DR на русском/узбекском).

- **instructor** или **pydantic** — гарантируют получение от LLM строго валидированного JSON.
- **sentence-transformers** _(или OpenAI Embeddings)_ — генерация векторных представлений (эмбеддингов) для поиска похожих новостей и склейки повторяющихся сюжетов.

---

## 4. База данных и Векторный поиск (Persistence)

- **PostgreSQL** + **pgvector** — универсальное решение «всё в одном»:
- Реляционные таблицы для хранения постов, источников, тегов, пользователей.
- Расширение `pgvector` для хранения векторных эмбеддингов и быстрого поиска дубликатов новостей через косинусное сходство прямо в SQL.

- **SQLAlchemy (v2.0 Async)** или **Tortoise-ORM** — асинхронные ORM для удобной работы с БД.
- **Alembic** — управление миграциями схемы БД.

---

## 5. Доставка контента и Backend (Delivery & API)

- **aiogram 3.x** — для создания Telegram-бота (автопостинг в канал, персональные уведомления по тегам, дайджесты).
- **FastAPI** — если планируется REST API для веб-сайта или мобильного приложения.
- **uv** — ультрабыстрый менеджер зависимостей и окружения на Rust (замена `pip`, `poetry` и `pipenv`).

---

## Итоговая архитектура стека

| Слой                  | Выбранный инструмент                          | Альтернатива      |
| --------------------- | --------------------------------------------- | ----------------- |
| **Язык & Менеджер**   | Python 3.12+ / `uv`                           | Poetry            |
| **Сбор Telegram**     | `Telethon` (Async)                            | Pyrogram          |
| **Сбор Web / RSS**    | `httpx` + `selectolax` + `feedparser`         | BeautifulSoup4    |
| **Планировщик**       | `APScheduler`                                 | ARQ + Redis       |
| **AI / Суммаризация** | `gpt-4o-mini` / `Gemini Flash` + `instructor` | Ollama (локально) |
| **БД & Векторы**      | `PostgreSQL` + `pgvector`                     | Qdrant / Redis    |
| **ORM & Миграции**    | `SQLAlchemy 2.0 Async` + `Alembic`            | Tortoise-ORM      |
| **Бот / API**         | `aiogram 3.x` / `FastAPI`                     | Litestar          |
