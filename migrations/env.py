import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from extensions import db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目標 metadata 用 extensions.db.metadata
target_metadata = db.metadata

# env.py 讀取環境變數 DATABASE_URL；程序環境裡還沒有時，改讀專案目錄的 .env
database_url = os.getenv("DATABASE_URL")
if not database_url:
    base_dir = Path(__file__).resolve().parent.parent
    dotenv_path = base_dir / ".env"
    if dotenv_path.is_file():
        load_dotenv(dotenv_path)
        database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("未設定 DATABASE_URL 環境變數，請在系統環境變數或專案目錄的 .env 中提供 PostgreSQL 連線字串。")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("未設定 DATABASE_URL 環境變數，請在系統環境變數或專案目錄的 .env 中提供 PostgreSQL 連線字串。")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
