"""Alembic environment script.

This is a Python script that is run whenever
the alembic migration tool is invoked.
At the very least, it contains instructions to configure
and generate a SQLAlchemy engine, procure a connection
from that engine along with a transaction,
and then invoke the migration engine,
using the connection as a source of database connectivity.

The env.py script is part of the generated environment so that
the way migrations run is entirely customizable.
The exact specifics of how to connect are here, as well as
the specifics of how the migration environment is invoked.
The script can be modified so that multiple engines
can be operated upon, custom arguments can be passed
into the migration environment, application-specific libraries
and models can be loaded in and made available.

Alembic includes a set of initialization templates which
feature different varieties of env.py for different use cases.

To avoid storing db credentials, this scripts will rely on envvars
declared in the config class of our project.

Since we are using our app modules, alembic need to be executed as
our app user with the PYTHONPATH envvar configured.

It means that our deployment process must have the following order:
    1. Deploy release code
    2. Create new virtualenv
    3. Install requirements in new virtualenv
    4. Stop app service(s)
    5. *Migrate DB*
    6. Start app service(s)
"""

from logging.config import fileConfig

from alembic import context
from db.migrate.utils import *

from app.common import db
from app.common.config import Config as AppConfig

# Alembic Config object, providing access to the values within the alembic.ini file.
config = context.config

fileConfig(config.config_file_name)


def migrate_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=AppConfig.SQLALCHEMY_DATABASE_URI,
        target_metadata=db.Model.metadata,
        literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def migrate_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = db.engine()

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=db.Model.metadata
        )

        with context.begin_transaction():
            context.run_migrations()


def migrate():
    """Run migration."""
    return migrate_offline() if context.is_offline_mode() else migrate_online()


migrate()
