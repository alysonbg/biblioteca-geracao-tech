#!/bin/sh
set -e

# Executa migrações no banco de dados (RDS)
echo "Aplicando migrações do banco de dados..."
uv run python manage.py migrate --noinput

echo "Iniciando aplicação..."
exec "$@"
