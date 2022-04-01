"""API package initializer."""

from flask import Flask
from flask_restful import Api

from app.common.config import Config
from app.common.utils import log_handler


def create_app(config=None):
    """Flask Application Factory."

    Create the flask object and initialize the rest
    of the needed object (api, db etc...).
    The flask object implements a WSGI application and acts
    as the central object.
    Once it is created it will act as a central registry for
    the rest of the application.

    :parameters:
         - config (object): Object containing configuration keys
                            (default: common.config.Config).

    :returns:
        - app (flask.Flask): The instantiated Flask app object.
    """

    app = Flask('api')

    app.config.from_object(config or Config)

    # Once created, that object then contains all
    # the functions and helpers from both
    # sqlalchemy and sqlalchemy.orm.
    app.db = SQLAlchemy(app)

    handler = log_handler('api')
    # Since flask 1.0 using pre-fork server like gunicorn,
    # creates duplicate logger handlers.
    if handler.name not in [h.name for h in app.logger.handlers if h.name is not None]:
        app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    app_api = Api(app, prefix='/api/v1')

    app_api.add_resource(
        # Add resources from the api.resources module here,
        # ex:
        # resources.User,
        # 'api/<string:username>'
    )

    return app
