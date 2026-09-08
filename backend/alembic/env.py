from pathlib import Path
import sys

from alembic import context
from sqlalchemy import create_engine, pool


# Get the backend directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Add backend/src to Python path
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from infrastructure.settings import settings


config = context.config

# Use the database URL from application settings
DATABASE_URL = settings.database_url

target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    connectable = create_engine(
        DATABASE_URL,
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