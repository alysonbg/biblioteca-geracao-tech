## Esse projeto é uma versão simplicada de uma api de uma biblioteca

## Stack  e Ferramentas:
- **Linguagem: Python 3.15
- **Framework: Django
- ** Testes: Unittest do django
- ** Containers: podman compose

## Como rodar o projeto:
- ** Rode os comandos dentro do container ou utilize podman compose web
- **Utilize o comando podman compose
- **Rodar tests: uv run python manage.py test
- **Rodar flake8? uv run flake8

## Estrutura do projeto:
- **biblioteca é a pasta de projeto do django. Evitar adicionar lógica e endpoints aqui.
- **api é o app da api. Todos os models, views e routers da api de biblioteca devem ficar nessa pasta.

## Padrões de projeto:
-- Aplique SOLID no código gerado
-- Aplique Clean Code
-- Evite repetir código
-- Teste sempre o happy path e as excessões.