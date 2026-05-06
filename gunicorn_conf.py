import multiprocessing
import os

# Gunicorn configuration file

# Bind to all interfaces on port 8000
bind = os.getenv("BIND", "0.0.0.0:8000")

# Worker processes
# Formula: (2 x $num_cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class for async performance
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout for worker processes
timeout = 120

# Keep-alive connections
keepalive = 5

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Max requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Preload app code before worker processes are forked
preload_app = True
