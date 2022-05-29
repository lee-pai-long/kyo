"""Clearing House config module.

:contains:
    - Config: Class containing configuration keys.
"""

# IDEA: Maybe use the ChainMap(https://goo.gl/AP8PZb)
# class to dynamize loading conf...

import os
# Uncomment when defining GUNICORN_USER and GUNICORN_GROUP
# import pwd


class Config:
    """Flask configuration object to use with app.config.from_object.

    Some of the configuration item set here can be override
    by the corresponding envvars:
        - APP_LOG_LEVEL: DEBUG
        - APP_LOG_DIRECTORY: /opt/app/logs
                            (symlinked by /var/log/app/logs)
        - APP_CONF_DIR: /etc/app/
        - FLASK_DEBUG: False
        - APP_DB_USER: app
        - APP_DB_PASSWORD: app
        - APP_DB_NAME: app
        - SQLALCHEMY_TRACK_MODIFICATIONS: False
        - SQLALCHEMY_ECHO: False
        - GUNICORN_BIND: /var/run/app/gunicorn.socket
        - GUNICORN_BACKLOG: 2048
        - GUNICORN_WORKERS: 1
        - GUNICORN_WORKER_CLASS: sync
        - GUNICORN_THREADS: 1
        - GUNICORN_WORKER_CONNECTIONS: 1000
        - GUNICORN_MAX_REQUESTS: 0
        - GUNICORN_MAX_REQUESTS_JITTER: 0
        - GUNICORN_TIMEOUT: 30
        - GUNICORN_GRACEFUL_TIMEOUT: 30
        - GUNICORN_KEEPALIVE: 2
        - GUNICORN_LIMIT_REQUEST_LINE: 4096
        - GUNICORN_LIMIT_REQUEST_FIELDS: 100
        - GUNICORN_LIMIT_REQUEST_FIELD_SIZE: 8190
        - GUNICORN_RELOAD: 0(False)
        - GUNICORN_RELOAD_ENGINE: auto
        - GUNICORN_SPEW: 0(False)
        - GUNICORN_CHECK_CONFIG: 0(False)
        - GUNICORN_PRELOAD_APP: 0(False)
        - GUNICORN_CHDIR: /opt/app/
        - GUNICORN_DAEMON: 1(True)
        - GUNICORN_PIDFILE: /var/run/app/gunicorn.pid
        - GUNICORN_WORKER_TMP_DIR: /tmp
        - GUNICORN_USER: app
        - GUNICORN_UMASK: 0
        - GUNICORN_INITGROUPS: 0(False)
        - GUNICORN_FORWARDED_ALLOW_IPS: 127.0.0.1
        - GUNICORN_ACCESSLOG: /var/log/app/gunicorn_access.log
        - GUNICORN_ERRORLOG: /var/log/app/gunicorn_error.log
        - GUNICORN_CAPTURE_OUTPUT: 0(False)
        - GUNICORN_ACCESS_LOG_FORMAT:
            '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

    Gunicorn configuration is define this way to enable a "12Factorish"
    configuration management. To see the full configurations documentation
    go to https://goo.gl/CUvWEU.

    The gunicorn_sendfile configuration is forcibly set to False
    to disable it because if the setting is None(default)
    it will read the envvar SENDFILE which is not
    specifically a Gunicorn one. (see: https://goo.gl/m8Pwsz).

    The following gunicorn configuration keys are not set through:
        - raw_env: Only useful in cli to surcharge app configuration.
        - tmp_upload_dir: Useless and risk to disappear.
        We don't want to change those without a redesign:
            - logger_class
            - logconfig
            - syslog_addr
            - syslog
            - syslog_prefix
            - syslog_facility
            - enable_stdio_inheritance
            - statsd_host
            - statsd_prefix
            - pythonpath
            - paste
            - proxy_protocol
            - proxy_allow_ips
        SSL in only activated at nginx level:
            - keyfile
            - certfile
            - ssl_version
            - cert_reqs
            - ca_certs
            - secure_scheme_header
            - suppress_ragged_eofs
            - do_handshake_on_connect
            - ciphers
        We'll never use PasteDeploy without creating a new release:
            - proc_name
            - default_proc_name
            - raw_paste_global_conf

        Flask for the most part has fine default configuration,
        the only configuration we switch is TRAP_HTTP_EXCEPTIONS
        to allow us to add custom  error handler
        (for example for custom HTTP error 519).
    """

    # pylint: disable=too-few-public-methods
    #       This class is intended to be use this way
    #       (see: https://goo.gl/yPPhyQ).

    # --- Constants
    RUN_DIRECTORY = os.environ.get('APP_RUN_DIRECTORY', '/var/run/app')
    LOG_DIRECTORY = os.environ.get('APP_LOG_DIRECTORY', '/var/log/app')

    # --- App configuration.
    TESTING = os.environ.get('APP_TESTING', False)
    LOG_DIR = os.path.join(os.environ['HOME'], 'log')
    LOG_LEVEL = os.environ.get('APP_LOG_LEVEL', 'DEBUG').upper()

    # --- Flask configuration.
    DEBUG = bool(int(os.environ.get('FLASK_DEBUG', False)))

    # --- Database configuration.
    DB_USER = os.environ.get('APP_DB_USER', 'app')
    DB_PASSWORD = os.environ.get('APP_DB_PASSWORD', 'app')
    DB_NAME = os.environ.get('APP_DB_NAME', 'App')
    # TODO: Change to postgres.
    DB_SOCKET = os.environ.get('APP_DB_SOCKET', '/var/run/mysqld/mysqld.sock')
    # WARNING: This two following variables combination fails to create
    #          the sqlite database in the root directory of the project,
    #          it instead creates it in app/common.
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DATABASE_FILE = os.environ.get(
        "APP_DB", os.path.join(ROOT_DIR, "app.db")
    )
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{APP_DATABASE_FILE}"

    SQLALCHEMY_TRACK_MODIFICATIONS = bool(int(os.environ.get(
        'SQLALCHEMY_TRACK_MODIFICATIONS',
        False
    )))

    SQLALCHEMY_ECHO = bool(int(os.environ.get('SQLALCHEMY_ECHO', False)))

    # --- Gunicorn configuration.
    GUNICORN_BIND = os.environ.get(
        'GUNICORN_BIND',
        # pylint: disable=consider-using-f-string
        "unix:{path}".format(path=os.path.join(RUN_DIRECTORY, 'gunicorn.sock'))
    )
    GUNICORN_BACKLOG = os.environ.get('GUNICORN_BACKLOG', 2048)
    GUNICORN_WORKERS = os.environ.get('GUNICORN_WORKERS', 1)
    GUNICORN_WORKER_CLASS = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')
    GUNICORN_THREADS = os.environ.get('GUNICORN_THREADS', 1)
    GUNICORN_WORKER_CONNECTIONS = os.environ.get(
        'GUNICORN_WORKER_CONNECTIONS', 1000
    )
    GUNICORN_MAX_REQUESTS = os.environ.get('GUNICORN_MAX_REQUESTS', 0)
    GUNICORN_MAX_REQUESTS_JITTER = os.environ.get(
        'GUNICORN_MAX_REQUESTS_JITTER', 0
    )
    GUNICORN_TIMEOUT = os.environ.get('GUNICORN_TIMEOUT', 30)
    GUNICORN_GRACEFUL_TIMEOUT = os.environ.get(
        'GUNICORN_GRACEFUL_TIMEOUT', 30
    )
    GUNICORN_KEEPALIVE = os.environ.get('GUNICORN_KEEPALIVE', 2)
    GUNICORN_LIMIT_REQUEST_LINE = os.environ.get(
        'GUNICORN_LIMIT_REQUEST_LINE', 4096
    )
    GUNICORN_LIMIT_REQUEST_FIELDS = os.environ.get(
        'GUNICORN_LIMIT_REQUEST_FIELDS', 100
    )
    GUNICORN_LIMIT_REQUEST_FIELD_SIZE = os.environ.get(
        'GUNICORN_LIMIT_REQUEST_FIELD_SIZE',
        8190
    )
    GUNICORN_RELOAD = bool(int(os.environ.get('GUNICORN_RELOAD', False)))
    GUNICORN_RELOAD_ENGINE = os.environ.get('GUNICORN_RELOAD_ENGINE', 'auto')
    GUNICORN_SPEW = bool(int(os.environ.get('GUNICORN_SPEW', False)))
    GUNICORN_CHECK_CONFIG = bool(int(os.environ.get(
        'GUNICORN_CHECK_CONFIG', False
    )))
    GUNICORN_PRELOAD_APP = bool(int(os.environ.get(
        'GUNICORN_PRELOAD_APP', False
    )))
    # If the sendfile setting is None it will read the envvar SENDFILE,
    # So we force the value to force disabling it set
    # (see: https://goo.gl/m8Pwsz).
    GUNICORN_SENDFILE = False
    GUNICORN_CHDIR = os.environ.get(
        'GUNICORN_CHDIR',
        os.path.join(os.environ['HOME'], 'current/app')
    )
    GUNICORN_DAEMON = bool(int(os.environ.get('GUNICORN_DAEMON', True)))
    GUNICORN_PIDFILE = os.environ.get(
        'GUNICORN_PIDFILE',
        os.path.join(RUN_DIRECTORY, 'gunicorn.pid')
    )
    GUNICORN_WORKER_TMP_DIR = os.environ.get(
        'GUNICORN_WORKER_TMP_DIR',
        os.path.join(os.path.sep, 'tmp')
    )
    # Uncomment when you can create an app user in the target system.
    # GUNICORN_USER = os.environ.get(
    #     'GUNICORN_USER', pwd.getpwnam('app').pw_uid
    # )
    # GUNICORN_GROUP = os.environ.get(
    #     'GUNICORN_GROUP',
    #     pwd.getpwnam('app').pw_gid
    # )
    GUNICORN_UMASK = os.environ.get('GUNICORN_UMASK', 0)
    GUNICORN_INITGROUPS = bool(int(os.environ.get(
        'GUNICORN_INITGROUPS', False
    )))
    GUNICORN_FORWARDED_ALLOW_IPS = os.environ.get(
        'GUNICORN_FORWARDED_ALLOW_IPS',
        '127.0.0.1'
    )
    GUNICORN_ACCESSLOG = os.environ.get(
        'GUNICORN_ACCESSLOG',
        os.path.join(LOG_DIR, 'gunicorn_access.log')
    )
    GUNICORN_ERRORLOG = os.environ.get(
        'GUNICORN_ERRORLOG',
        os.path.join(LOG_DIR, 'gunicorn_error.log')
    )
    GUNICORN_ACCESS_LOG_FORMAT = os.environ.get(
        'GUNICORN_ACCESS_LOG_FORMAT',
        '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
    )
    GUNICORN_LOGLEVEL = os.environ.get('GUNICORN_LOGLEVEL', LOG_LEVEL.lower())
    GUNICORN_CAPTURE_OUTPUT = bool(int(os.environ.get(
        'GUNICORN_CAPTURE_OUTPUT',
        False
    )))
