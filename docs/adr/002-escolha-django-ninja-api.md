# ADR 002: Escolha do Django Ninja para Desenvolvimento da API

## Status
Aceito

## Contexto
Após a escolha do Django como framework base, precisávamos definir a melhor abordagem para construir a API REST. A documentação automática da API é um requisito essencial para facilitar a integração e manutenção do sistema, permitindo que desenvolvedores frontend e integradores compreendam rapidamente os endpoints disponíveis.

## Decisão
Decidimos utilizar o Django Ninja para construir a API REST do projeto.

## Justificativa
O Django Ninja oferece integração nativa com OpenAPI (anteriormente Swagger), proporcionando:

- **Documentação automática**: Geração automática de documentação OpenAPI 3.0 a partir do código
- **Interface interativa**: Swagger UI integrado para testar endpoints diretamente no navegador
- **Type hints Python**: Validação baseada em type hints e Pydantic, garantindo type safety
- **Performance**: Arquitetura assíncrona e performance comparável ao FastAPI
- **Integração com Django**: Aproveitamento total do ORM, autenticação e middleware do Django
- **Schema validation**: Validação automática de requests e responses usando Pydantic schemas
- **Zero configuração adicional**: OpenAPI disponível sem necessidade de configurações complexas

A documentação OpenAPI fica automaticamente disponível em `/api/docs`, facilitando o desenvolvimento e testes.

## Consequências

### Positivas
- Documentação da API sempre atualizada e sincronizada com o código
- Redução de erros através de validação automática de tipos
- Interface amigável para testar endpoints sem ferramentas externas
- Melhor experiência de desenvolvimento com autocomplete e type checking
- Facilita onboarding de novos desenvolvedores
- Padrão OpenAPI amplamente adotado pela indústria

### Negativas
- Biblioteca relativamente mais nova comparada ao Django REST Framework
- Comunidade menor que o DRF (Django REST Framework)
- Menos plugins e extensões de terceiros disponíveis
- Curva de aprendizado para desenvolvedores acostumados com DRF

## Alternativas Consideradas
- **Django REST Framework (DRF)**: Framework mais maduro, mas requer configuração adicional (drf-spectacular) para gerar documentação OpenAPI completa
- **FastAPI com integração Django**: Melhor performance, mas adiciona complexidade na integração com Django ORM e autenticação
- **API views nativas do Django**: Mais simples, mas sem validação automática e documentação integrada

## Notas de Implementação
A documentação OpenAPI está acessível em:
- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc` (se configurado)
- **Schema JSON**: `/api/openapi.json`
