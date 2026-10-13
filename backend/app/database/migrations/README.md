# Migrations

This folder is intended for [Alembic](https://alembic.sqlalchemy.org/) migration
scripts.

To initialize Alembic once the project dependencies are installed:

```bash
cd backend
alembic init app/database/migrations
```

Then point `sqlalchemy.url` in `alembic.ini` (or `env.py`) at
`app.core.config.settings.DATABASE_URL`, and generate your first migration:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```
