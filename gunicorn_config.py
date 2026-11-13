"""
Configuração do Gunicorn para o projeto Biblioteca.
"""
import multiprocessing
import os

# Endereço e porta
bind = "0.0.0.0:8000"

# Número de workers
# Recomendação: (2 x $num_cores) + 1
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Tipo de worker
worker_class = "sync"

# Número de threads por worker (para worker_class sync)
threads = int(os.getenv("GUNICORN_THREADS", 1))

# Timeout para requisições (em segundos)
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))

# Tempo máximo de vida de um worker (em segundos)
# Previne memory leaks ao reciclar workers periodicamente
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 50))

# Keep-alive
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 2))

# Logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # - significa stdout
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")    # - significa stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Configurações de segurança
limit_request_line = int(os.getenv("GUNICORN_LIMIT_REQUEST_LINE", 4094))
limit_request_fields = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELDS", 100))
limit_request_field_size = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", 8190))

# Pre-load da aplicação (melhora performance mas usa mais memória)
preload_app = os.getenv("GUNICORN_PRELOAD", "false").lower() == "true"

# Graceful timeout
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 30))
