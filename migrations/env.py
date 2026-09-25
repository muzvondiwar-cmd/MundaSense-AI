from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from alembic import context
from sqlalchemy import engine_from_config, pool

from mundasense.config import AppConfig
from mundasense.storage.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

configured_url = os.getenv("MUNDASENSE_DATABASE_URL")
if not configured_url:
    path = AppConfig.from_env().database_path.resolve().as_posix()
    configured_url = f"sqlite+pysqlite:///{path}"
config.set_main_option("sqlalchemy.url", configured_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
