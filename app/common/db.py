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
# pylint: disable=too-few-public-methods

import json
import logging
from contextlib import contextmanager
from datetime import date, datetime

import sqlalchemy as sql
from inflection import pluralize
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from app.common import errors as err
from app.common.config import Config
from app.common.utils import is_date


def engine(uri=None):
    """Create a database engine.

    :parameters:
        - uri: Sql uri (default: Config.SQLALCHEMY_DATABASE_URI).

    :returns:
        - sqlalchemy.engine.Engine
    """
    uri = uri or Config.SQLALCHEMY_DATABASE_URI
    return sql.create_engine(uri)


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
    connection = engine().connect()
    session = Session(bind=connection)  # pylint: disable=redefined-outer-name

    yield session

    session.close()
    connection.close()


class Base:
    """Class to use with SQLAlchemy declaration_base().

    With the addition of active records pattern methods.

    Subclass must still declare fields using the sql.Column
    class as usual with SQLAlchemy.

    methods:
        - save (instance): insert or update.
        - fetch (instance): select an model from id.
        - select (class): select any entities from matched columns.
        - delete (instance): delete an model from id.
        - to_dict (instance): return model as dict.
        - to_json (instance): return model as json.
        - from_dict (class): create an model from dict.
        - from_json (class): create an model from json.
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
        """Insert or update model in DB.

        :usages:
            >>> my_model = MyModel()
            >>> my_model.param1 = True
            >>> my_model.save()
            >>> # or
            >>> my_model.save(logger='backend')
            >>> # or
            >>> somemodel = MyModel(param2=False).save()

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to root logger)

        :returns:
            - self

        :raises:
            - app.common.errors.SavingModelFailed
        """
        log = logging.getLogger(logger)

        with session() as db:

            # Merge existing model in case of update.
            if self.id is not None:
                self = db.merge(self)  # pylint: disable=self-cls-assignment

            log.debug("Adding a %s to transaction", self.__class__.__name__)
            db.add(self)

            try:
                log.debug(
                    "Committing a %s to database",
                    self.__class__.__name__,
                )
                db.commit()

            except SQLAlchemyError as e:
                log.error(
                    "Unable to save a %s: %s",
                    self.__class__.__name__,
                    str(e)
                )
                db.rollback()
                raise err.UnableToSaveModelInDB(str(e)) from e

            except Exception as e:
                log.critical(
                    "Unknown error while saving a %s: %s",
                    self.__class__.__name__,
                    str(e)
                )
                db.rollback()
                raise err.SavingModelFailed(str(e)) from e

            log.debug(
                "%s %s saved to database",
                self.__class__.__name__,
                self.id
            )
            return self

    @classmethod
    def fetch(cls, logger='', id=None):  # pylint: disable=redefined-builtin
        """Fetch existing model based on id.

        :usages:
            >>> a_model = SomeModel(id=some_id).fetch()
            >>> # or
            >>> my_model = SomeModel()
            >>> my_model.id = some_id
            >>> my_model.fetch()
            >>> # or
            >>> some_model = SomeModel().fetch(id=some_id)

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to root logger)

            - id (int or str): primary key of the model to fetch
                               (optional, default to self.id)
        :returns:
            - self

        :raises:
            - app.common.errors.InvalidModelId
            - app.common.errors.UnknownModelId
            - app.common.errors.FetchingModelFailed
        """
        log = logging.getLogger(logger)

        if id is None or not isinstance(id, int):
            raise err.InvalidModelId("Model's id must be of type int")

        with session() as db:

            try:
                log.debug("Fetching %s %s", cls.__name__, id)

                model = db.query(cls).filter_by(id=id).one()

            except NoResultFound as e:
                log.error("Unknown %s %s", cls.__name__, id)
                # NOTE: Intuitively rolling back on a select seems unnecessary,
                # but somehow sqlalchemy get stuck without it...
                db.rollback()
                raise err.UnknownModelId from e

            except SQLAlchemyError as e:
                log.error(
                    "Unable to fetch %s %s: %s",
                    cls.__name__,
                    id,
                    str(e)
                )
                db.rollback()
                raise err.UnableToFetchModelFromDB(str(e)) from e

            except Exception as e:
                log.critical(
                    "Unknown error while fetching %s %s: %s",
                    cls.__name__,
                    id,
                    str(e)
                )
                db.rollback()
                raise err.FetchingModelFailed(str(e)) from e

            log.debug("%s %s fetched from database", cls.__name__, id)
            return model

    @classmethod
    def select(cls, logger='', limit=None, **kwargs):
        """Select any entities from matching attributes.

        The kwargs passed are used as in a where clause.

        :usages:
            >>> some_models = SomeModel.select(attr1='toto', attr2='titi')

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to root logger)
            - limit (int): Number of element to select.

        :returns:
            - selected (list): a list of selected rows (may be empty)

        :raises:
            - app.common.errors.InvalidModelAttribute
            - app.common.errors.SelectingModelsFailed
        """
        log = logging.getLogger(logger)

        with session() as db:

            try:
                log.debug(
                    "Selecting %s %s",
                    cls.__name__,
                    # pylint: disable=consider-using-f-string
                    ', '.join([
                        "{arg}={val}".format(arg=k, val=repr(v))
                        for k, v in sorted(kwargs.items())
                    ])
                )
                selected = db.query(cls).filter_by(**kwargs).limit(limit).all()

            except InvalidRequestError as e:
                log.error(
                    "Invalid argument(s) supplied for selecting %ss",
                    cls.__name__
                )
                raise err.InvalidModelAttribute(str(e)) from e

            except SQLAlchemyError as e:
                log.error(
                    "Unable to select from %s: %s",
                    cls.__name__,
                    str(e)
                )
                raise err.UnableToSelectFromDB(str(e)) from e

            except Exception as e:
                log.critical(
                    "Unknown error while selecting on %s: %s",
                    cls.__name__,
                    str(e)
                )
                raise err.SelectingModelsFailed(str(e)) from e

        return selected

    # FIXME: This method doesn't work when running the corresponding tests,
    #          they fail with the following type of error:
    #  Instance '<Dummy at 0x7fd8d3c73b20>' is not persisted
    # It seems like the session.delete() method is not use correctly,
    # or at least it doesn't work.
    def delete(self, logger=''):
        """Delete model from DB.

        :usages:
            >>> my_model = MyModel()
            >>> my_model_id = my_model.id
            >>> model.delete()
            >>> queried_model = my_model.query.get(my_model_id)
            >>> queried_model is None
            True

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to root logger)
        :returns:
            - True if the model has been successfully deleted

        :raises:
            - app.common.errors.UnableToDeleteModel
        """
        log = logging.getLogger(logger)

        with session() as db:

            try:
                log.debug("Deleting %s %s", self.__class__.__name__, self.id)

                db.delete(self)
                db.commit()

            except SQLAlchemyError as e:
                log.error(
                    "Unable to delete %s %s: %s",
                    self.__class__.__name__,
                    self.id,
                    str(e)
                )
                db.rollback()
                raise err.UnableToDeleteModelFromDB(str(e)) from e

            except Exception as e:
                log.critical(
                    "Unknown error while fetching %s %s: %s",
                    self.__class__.__name__,
                    self.id,
                    str(e)
                )
                db.rollback()
                raise err.DeletingModelFailed(str(e)) from e

        return True

    def to_dict(self, logger=''):
        """Convert model to dict containing model columns.

        :usages:
            >>> class Dummy(db.Model):
            >>>     id = sql.Column(sql.Integer, primary_key=True)
            >>>     name = sql.Column(sql.String(80), nullable=False)
            >>>     birthdate = sql.Column(sql.Date, nullable=False)
            >>>
            >>> dummy = Dummy(name='Jon', birthdate=datetime.date(1986, 4, 4))
            >>> dummy.to_dict()
            {'name': 'Jon', 'birthdate': datetime.date(1986, 4, 4)}

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to root logger)

        :returns:
            - a dict containing the model attributes, ex:
            {'name': 'Jon', 'birthdate': datetime.date(1986, 4, 4)}}

        """
        log = logging.getLogger(logger)

        log.debug(
            "Converting model %s with id %s to dict",
            self.__class__.__name__,
            self.id
        )

        converted = {
            key: value
            for key, value
            in self.__dict__.items()
            if not key.startswith('_')
        }

        log.debug(
            "Converted model %s with id %s to dict: %s",
            self.__class__.__name__,
            self.id,
            converted
        )
        return converted

    def to_json(self, logger=''):
        """Convert model to json containing model columns.

        :usages:
            >>> class Dummy(db.Model):
            >>>     id = sql.Column(sql.Integer, primary_key=True)
            >>>     name = sql.Column(sql.String(80), nullable=False)
            >>>     birthdate = sql.Column(sql.Date, nullable=False)
            >>>
            >>> dummy = Dummy(name='Jon', birthdate=datetime.date(1986, 4, 4))
            >>> dummy.to_json()
            {"name": "Jon", "birthdate": "1986-04-04"}

        :parameters:
            - logger (string): name of the logger to use
                               (optional, default to root logger)
        :returns:
            - a json object representation of the model, ex:
            {"name": "Jon", "birthdate": "1986-04-04"}
        """
        log = logging.getLogger(logger)

        log.debug(
            "Converting model %s with id %s to json",
            self.__class__.__name__,
            self.id
        )

        to_convert = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, (date, datetime)):
                    to_convert[key] = value.isoformat()
                else:
                    to_convert[key] = value
        converted = json.dumps(to_convert)

        log.debug(
            "Converted model %s with id %s to json: %s",
            self.__class__.__name__,
            self.id,
            converted
        )
        return converted

    @classmethod
    def from_dict(cls, dict_to_convert, logger=''):
        """Convert given dict to model.

        :usages:
            >>> dummy = {
            >>>     'name': 'Jon',
            >>>     'birthdate': "1986-04-04"
            >>> }
            >>>
            >>> dummy_instance = Dummy.from_dict(dummy)
            >>> str(dummy_instance)
            Dummy(id=1234, name='Jon', birthdate=datetime.date(1986, 4, 4))

        :parameters:
            - dict_to_convert (dict): The dict to convert to a model object,
                the dict must contain the same attributes as expected by the
                model class instantiation
                If one of the attribute is of type date or datetime, it must
                be given in iso format following ISO 8601.
            - logger (string): name of the logger to use
                               (optional, default to root logger)
        :returns:
            - a model object with the attributes machting the dict attributes
            Dummy(id=1234, name='Jon', birthdate=datetime.date(1986, 4, 4))
        """
        log = logging.getLogger(logger)

        log.debug(
            "Converting dict %s to model %s",
            dict_to_convert,
            cls.__name__,
        )

        to_convert = {}
        for key, value in dict_to_convert.items():
            if is_date(value):
                if 'T' in value:
                    to_convert[key] = datetime.fromisoformat(value)
                else:
                    to_convert[key] = date.fromisoformat(value)
            else:
                to_convert[key] = value

        log.debug(
            "Converted dict %s to model %s",
            dict_to_convert,
            cls.__name__,
        )

        return cls(**to_convert)

    @classmethod
    def from_json(cls, json_to_convert, logger=''):
        """Convert given json string to model.

        :usages:
            >>> dummy = '{"name": "Jon", "birthdate": "1986-04-04"}'
            >>>
            >>> dummy_instance = Dummy.from_json(dummy)
            >>> str(dummy_instance)
            Dummy(id=1234, name='Jon', birthdate=datetime.date(1986, 4, 4))

        :parameters:
            - json_to_convert (json): The json string to convert
                to a model object, the json object must contain
                the same attributes as expected by the model
                class instantiation
                If one of the attribute is of type date or datetime, it must
                be given in iso format following ISO 8601.
            - logger (string): name of the logger to use
                               (optional, default to root logger)
        :returns:
            - a model object with the attributes machting the json attributes
            Dummy(id=1234, name='Jon', birthdate=datetime.date(1986, 4, 4))
        """
        log = logging.getLogger(logger)

        log.debug(
            "Converting json %s to model %s",
            json_to_convert,
            cls.__name__,
        )

        try:
            dict_to_convert = json.loads(json_to_convert)
        except json.JSONDecodeError as e:
            log.error(
                "Unable to create model %s from json string %s, error: %s",
                cls.__name__, json_to_convert, str(e)
            )
            raise err.UnableToCreateModelFromJSON(str(e)) from e


        log.debug(
            "Converted json %s to model %s",
            json_to_convert,
            cls.__name__,
        )

        return cls.from_dict(dict_to_convert)

    def __repr__(self):
        """Return printable representation of herited class objects."""
        # pylint: disable=consider-using-f-string
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
