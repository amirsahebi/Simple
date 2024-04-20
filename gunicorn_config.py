from decouple import config as env_config

# ------- Debugging -------

DEBUG = env_config("DEBUG", False, cast=bool)
reload = True if DEBUG else False

# ------- Logging -------

accesslog = "-"
errorlog = "-"
loglevel = "debug" if DEBUG else "info"

# ------- Security -------

limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# ------- Server Mechanics -------

preload_app = False
forwarded_allow_ips = "*"
proxy_allow_ips = "*"

# ------- Server Socket -------

LOCAL = env_config("PHASE", "local") == "local"
host ="0.0.0.0"
port = "6500"
bind = ":{port}".format(port=port)
backlog = 2048

# ------- Worker Processes -------

# workers = multiprocessing.cpu_count() * 2 + 1
workers = 5
# worker_class = "gevent"
threads = 2
worker_connections = 1000
max_requests = 100
max_requests_jitter = 0
timeout = 120
# graceful_timeout = 30
