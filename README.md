# biblioteca-geracao-tech

[![CI/CD Pipeline](https://github.com/alysonbg/biblioteca-geracao-tech/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/alysonbg/biblioteca-geracao-tech/actions/workflows/ci-cd.yml)

Sistema de gerenciamento de biblioteca desenvolvido com Django.

## 🚀 Tecnologias

- Python 3.15
- Django 6.1.3
- Django Ninja (API REST)
- PostgreSQL 16
- Gunicorn (WSGI Server)
- Docker & Podman

## 📦 Servidor de Aplicação

O projeto utiliza **Gunicorn** como servidor WSGI para produção. O Gunicorn oferece:

- Alta performance e estabilidade
- Suporte a múltiplos workers
- Gerenciamento eficiente de conexões
- Configuração flexível via variáveis de ambiente

### Configuração do Gunicorn

O arquivo `gunicorn_config.py` contém todas as configurações do servidor. Você pode personalizar através das seguintes variáveis de ambiente no arquivo `.env`:

```bash
# Número de workers (padrão: CPU cores * 2 + 1)
GUNICORN_WORKERS=4

# Timeout para requisições em segundos
GUNICORN_TIMEOUT=30

# Máximo de requisições antes de reciclar o worker
GUNICORN_MAX_REQUESTS=1000

# Log level (debug, info, warning, error, critical)
GUNICORN_LOG_LEVEL=info

# Pre-load da aplicação (melhora performance)
GUNICORN_PRELOAD=false
```

### Executando com Gunicorn

**Com Docker/Podman Compose:**
```bash
podman-compose up
```

**Manualmente:**
```bash
uv run gunicorn biblioteca.wsgi:application --config gunicorn_config.py
```

**Para desenvolvimento (Django runserver):**
```bash
uv run python manage.py runserver
```

## 🏃 Como Rodar

1. Clone o repositório
2. Copie o arquivo `.env.example` para `.env` e configure as variáveis
3. Execute com Docker/Podman:
   ```bash
   podman-compose up --build
   ```

## 🧪 Testes

Execute os testes:
```bash
uv run python manage.py test
```

## 📝 Lint

Execute o Flake8:
```bash
uv run flake8
```