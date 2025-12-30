
from dotenv import load_dotenv
load_dotenv()


from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 🔽 추가: DB, Base, 모델 import
from db.database import Base, DATABASE_URL
from models import analysis  # ⚠️ 모델 전부 import (중요)

# Alembic Config object
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 🔽 핵심: autogenerate 대상 메타데이터
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # 🔽 DATABASE_URL 직접 주입
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # 🔽 여기!! alembic.ini 대신 코드에서 URL 주입
    config.set_main_option(
        "sqlalchemy.url",
        DATABASE_URL
    )

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()