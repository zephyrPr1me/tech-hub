# Smart Tech Hub Uzbekistan

Автономный сервис сбора, фильтрации и дайджеста IT/ИИ новостей Узбекистана.

## Стек

| Слой | Инструмент |
| --- | --- |
| Язык & менеджер | Python 3.14 / Poetry |
| Backend | FastAPI + Uvicorn |
| Сбор (следующие этапы) | Telethon, httpx, feedparser, selectolax |
| Планировщик (следующие этапы) | APScheduler |
| AI (следующие этапы) | OpenAI / Gemini + instructor |
| БД и векторы | PostgreSQL + pgvector, SQLAlchemy 2.0 Async, Alembic |

## Структура

```text
backend/
├── alembic.ini            # заглушка (alembic init — на следующем этапе)
├── alembic/
└── src/
    ├── main.py            # точка входа FastAPI
    ├── config.py
    ├── api/               # REST API (v1: endpoints, router, dependencies)
    ├── core/              # БД, безопасность
    ├── scrapers/          # telegram, rss, web
    ├── processor/         # дедупликация, планировщик
    ├── ai/                # LLM клиент, промпты, схемы
    ├── bot/               # Telegram-бот, паблишер
    ├── models/            # SQLAlchemy ORM
    └── schemas/           # Pydantic схемы API
test/
```

## Запуск

```bash
cp .env.example .env          # заполнить переменные
poetry install                # зависимости + dev-группа

# локально
poetry run uvicorn --app-dir backend/src main:app --reload

# или в Docker (app + Postgres/pgvector)
docker compose up --build
```

## Проверки

```bash
poetry run ruff check .
poetry run pytest
```
