"""Main entry point for our app.

This is the module that will be called by whatever app server
(uwsgi, gunicorn etc...).

The app server will only use the app instance present,
while the runner executed inside the __main__
will be used for in development mode.

This module also contain gunicorn configuration variable define in
the clearinghouse.config module.
Having one stop place for everything related to WSGI
allow us to declare one APP_WSGI envvar to use for
both the app instance and the gunicorn config to read.
"""

from app.api import create_app

app = create_app()

# --- Gunicorn configuration ---
bind = app.config['GUNICORN_BIND']
backlog = app.config['GUNICORN_BACKLOG']
workers = app.config['GUNICORN_WORKERS']
worker_class = app.config['GUNICORN_WORKER_CLASS']
threads = app.config['GUNICORN_THREADS']
worker_connections = app.config['GUNICORN_WORKER_CONNECTIONS']
max_requests = app.config['GUNICORN_MAX_REQUESTS']
max_requests_jitter = app.config['GUNICORN_MAX_REQUESTS_JITTER']
timeout = app.config['GUNICORN_TIMEOUT']
graceful_timeout = app.config['GUNICORN_GRACEFUL_TIMEOUT']
keepalive = app.config['GUNICORN_KEEPALIVE']
limit_request_line = app.config['GUNICORN_LIMIT_REQUEST_LINE']
limit_request_fields = app.config['GUNICORN_LIMIT_REQUEST_FIELDS']
limit_request_field_size = app.config['GUNICORN_LIMIT_REQUEST_FIELD_SIZE']
# NOTE: If this line highlight like a built-in,
#       it's because reload was in python 2
#       and your editor doesn't differentiate between the two version.
reload = app.config['GUNICORN_RELOAD']
reload_engine = app.config['GUNICORN_RELOAD_ENGINE']
spew = app.config['GUNICORN_SPEW']
check_config = app.config['GUNICORN_CHECK_CONFIG']
preload_app = app.config['GUNICORN_PRELOAD_APP']
chdir = app.config['GUNICORN_CHDIR']
daemon = app.config['GUNICORN_DAEMON']
pidfile = app.config['GUNICORN_PIDFILE']
worker_tmp_dir = app.config['GUNICORN_WORKER_TMP_DIR']
user = app.config['GUNICORN_USER']
group = app.config['GUNICORN_GROUP']
umask = app.config['GUNICORN_UMASK']
initgroups = app.config['GUNICORN_INITGROUPS']
forwarded_allow_ips = app.config['GUNICORN_FORWARDED_ALLOW_IPS']
accesslog = app.config['GUNICORN_ACCESSLOG']
access_log_format = app.config['GUNICORN_ACCESS_LOG_FORMAT']
errorlog = app.config['GUNICORN_ERRORLOG']
loglevel = app.config['GUNICORN_LOGLEVEL']
capture_output = app.config['GUNICORN_CAPTURE_OUTPUT']

if __name__ == '__main__':
    app.run()
