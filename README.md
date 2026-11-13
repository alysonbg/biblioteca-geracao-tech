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

## 📚 Documentação da API

A documentação interativa da API (OpenAPI/Swagger) está disponível em:

- **Swagger UI**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Schema OpenAPI JSON**: [http://localhost:8000/api/openapi.json](http://localhost:8000/api/openapi.json)

A documentação é gerada automaticamente através do Django Ninja e permite testar todos os endpoints diretamente no navegador.

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

## 📖 Documentação Arquitetural

As decisões arquiteturais do projeto estão documentadas em ADRs (Architecture Decision Records):

- [ADR 001: Escolha do Django como Framework Principal](docs/adr/001-escolha-django-framework.md)
- [ADR 002: Escolha do Django Ninja para Desenvolvimento da API](docs/adr/002-escolha-django-ninja-api.md)