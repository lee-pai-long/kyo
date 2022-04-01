"""App models declaration.

Model naming convention is singular PascalCase,
while Table in DB are plural PascalCase.

:contains:
    Base classes:
        - Base: Class to use with SQLAlchemy declaration_base().
        - Model: Actual base class to subclass for models.
    Models:
    Functions:
        - engine: Create a database engine.
        - session: Generate a database session.

"""
# pylint: disable=too-few-public-methods, logging-format-interpolation

# Standard.
import logging
import itertools
from contextlib import contextmanager

# External.
import sqlalchemy as sql
from inflection import pluralize
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import NullPool

# Internal.
from app.common import errors as err
from app.common.config import Config


def engine(uri=None):
    """Create a database engine.

    :parameters:
        - uri: Sql uri (default: Config.SQLALCHEMY_DATABASE_URI).

    :returns:
        - sqlalchemy.engine.Engine
    """
    uri = uri or Config.SQLALCHEMY_DATABASE_URI
    return sql.create_engine(uri, poolclass=NullPool)


@contextmanager
def session():
    """Generate a database session.

    :setup:
        - Create a database connection using URI
          define in Config.SQLALCHEMY_DATABASE_URI.
        - Create a database session.

    :yields:
        - a database session object.

    :teardown:
        - Close the session.
        - Close the connection.
    """
    # IDEA: Add a autocommit feature ?

    connection = engine().connect()
    session = Session(bind=connection, expire_on_commit=False)

    yield session

    session.close()
    connection.close()


# TODO: Check SQLAlchemy mixin
class Base:
    """Class to use with SQLAlchemy declaration_base().

    With the addition of active records pattern methods.

    Subclass must still declare fields using the sql.Column
    class as usual with SQLAlchemy.

    methods:
        - save (instance): insert or update.
        - fetch (instance): select an entity from id.
        - select (class): select any entities from matched columns.
        TODO: Implement the folowing methods:
        - drop (instance): delete an entity from id.
        - delete (class): delete any entities from matched columns.
        - to_dict (instance): return entity as dict.
        - to_json (instance): return entity as json.
        - from_dict (class): create an entity from dict.
        - from_json (class): create an entity from json.
    """

    # Default options to use with every model class tables in __table_args__
    __table_args = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_general_ci'
    }

    # Constraints attribute to old sql.Index etc...
    # Used to dynamically update __table_args__
    __constraints = None

    # Used to avoid trying to delete of insert views etc...
    _is_view = False

    @declared_attr
    def __table_args__(cls):  # pylint: disable=no-self-argument
        """Define generic __table_args__ attribute."""

        t_args = []
        if cls.__constraints:
            t_args.append(cls.__constraints)
        t_args.append(cls.__table_args)
        return tuple(t_args)

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        """Define generic __tablename__ attribute."""

        return pluralize(cls.__name__)

    def save(self, logger=''):
        """Insert or update entity in DB.

        :usages:
            >>> mymodel = MyModel()
            >>> mymodel.param1 = True
            >>> mymodel.save()
            >>> # or
            >>> mymodel.save(logger='backend')
            >>> # or
            >>> somemodel = MyModel(param2=False).save()

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to module name)

        :returns:
            - self

        :raises:
            - SavingModelFailed
        """

        log = logging.getLogger(logger)

        with session() as db:

            # Merge existing entity in case of update.
            if self.id is not None:
                self = db.merge(self)

            log.debug("Adding a {model} to transaction".format(
                model=self.__class__.__name__,
            ))
            db.add(self)

            try:
                log.debug("Committing a {model} to database".format(
                    model=self.__class__.__name__,
                ))
                db.commit()

            except SQLAlchemyError as e:
                log.error("Unable to save a {model}: {error}".format(
                    model=self.__class__.__name__,
                    error=str(e)
                ))
                db.rollback()
                raise err.SavingModelFailed(str(e))

            except Exception as e:
                log.critical(
                    "Unknown error while saving a {model}: {error}".format(
                        model=self.__class__.__name__,
                        error=str(e)
                    )
                )
                db.rollback()
                raise err.SavingModelFailed(str(e))

            log.info("{model} {id} saved to database".format(
                model=self.__class__.__name__,
                id=self.id
            ))
            return self

    def fetch(self, logger='', id=None):
        """Fetch existing entity based on id.

        if self.id is None and the id parameter is None,
        or if the id type doesn't match the table primary key type
        it will raise an InvalidModelId exception.

        :usages:
            >>> amodel = SomeModel(id=some_id).fetch()
            >>> # or
            >>> mymodel = SomeModel()
            >>> mymodel.id = some_id
            >>> mymodel.fetch()
            >>> # or
            >>> somemodel = SomeModel().fetch(id=some_id)

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to module name)

            - id (int or str): primary key of the entity to fetch
                               (optional, default to self.id)
        :returns:
            - self

        :raises:
            - InvalidModelId
            - UnknownModelId
            - FetchingModelFailed
        """

        log = logging.getLogger(logger)

        current_id = id or self.id

        if current_id is None:
            raise err.InvalidModelId("Entity's id must not be None")

        with session() as db:

            try:
                log.debug("Fetching {model} {id}".format(
                    model=self.__class__.__name__,
                    id=current_id
                ))
                self = db.query(self.__class__).filter_by(id=current_id).one()

            except NoResultFound:
                log.error("Unknown {model} {id}".format(
                    model=self.__class__.__name__,
                    id=current_id
                ))
                # NOTE: Intuitively rolling back on a select seems unnecessary,
                # but somehow sqlalchemy get stuck without it...
                db.rollback()
                raise err.UnknownModelId

            except SQLAlchemyError as e:
                log.error("Unable to fetch {model} {id}: {error}".format(
                    model=self.__class__.__name__,
                    id=current_id,
                    error=str(e)
                ))
                db.rollback()
                raise err.FetchingModelFailed(str(e))

            except Exception as e:
                log.critical(
                    "Unknown error while fetching {model} {id}: {error}".format(
                        model=self.__class__.__name__,
                        id=current_id,
                        error=str(e)
                    )
                )
                db.rollback()
                raise err.FetchingModelFailed(str(e))

            log.debug("{model} {id} fetched from database".format(
                model=self.__class__.__name__,
                id=current_id
            ))
            return self

    @classmethod
    def select(cls, logger='', limit=None, **kwargs):
        """Select any entities from matching attributes.

        The kwargs passed are used as in a where clause.

        :usages:
            >>> somemodels = SomeModel.select(attr1='toto', attr2='titi')

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to module name)
            - limit (int): Number of element to select.

        :returns:
            - selected (list): a list of selected rows (may be empty)

        :raises:
            - InvalidModelAttribute
            - SelectingModelsFailed
        """

        log = logging.getLogger(logger)

        with session() as db:

            try:
                log.debug("Selecting {model} {args}".format(
                    model=cls.__name__,
                    args=', '.join([
                        "{arg}={val}".format(arg=k, val=repr(v))
                        for k, v in sorted(kwargs.items())
                    ])
                ))
                selected = db.query(cls).filter_by(**kwargs).limit(limit).all()

            except InvalidRequestError as e:
                log.error("Invalid argument(s) supply for selecting {model}s".format(
                    model=cls.__name__
                ))
                raise err.InvalidModelAttribute(str(e))

            except SQLAlchemyError as e:
                log.error("Unable to select from {model}: {error}".format(
                    model=cls.__name__,
                    error=str(e)
                ))
                raise err.SelectingModelsFailed(str(e))

            except Exception as e:
                log.critical("Unknown erro while selecting on {model}: {error}".format(
                    model=cls.__name__,
                    error=str(e)
                ))
                raise err.SelectingModelsFailed(str(e))

        return selected

    def __repr__(self):
        """Return printable representation of herited class objects."""

        return "{class_name}({attributes})".format(
            class_name=self.__class__.__name__,
            attributes=', '.join([
                "{attribute}={value}".format(attribute=key, value=repr(val))
                for key, val in sorted(self.__dict__.items())
                if not key.startswith('_')
            ])
        )


# Actual base class to subclass to create models.
Model = declarative_base(cls=Base, bind=engine())

