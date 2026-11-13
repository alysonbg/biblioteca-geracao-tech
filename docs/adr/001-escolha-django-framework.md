# ADR 001: Escolha do Django como Framework Principal

## Status
Aceito

## Contexto
Para o desenvolvimento da API de biblioteca, precisávamos escolher um framework Python que proporcionasse produtividade e segurança. A autenticação e autorização são requisitos fundamentais para qualquer sistema de gerenciamento de biblioteca, onde diferentes tipos de usuários (administradores, bibliotecários, leitores) precisam de diferentes níveis de acesso.

## Decisão
Decidimos utilizar o Django como framework principal do projeto.

## Justificativa
O Django já vem com um sistema robusto de autenticação implementado nativamente, incluindo:

- **Sistema de usuários e permissões**: Gerenciamento completo de usuários, grupos e permissões
- **Autenticação segura**: Hash de senhas com PBKDF2, proteção contra ataques de timing
- **Middleware de autenticação**: Integração transparente com views e APIs
- **Admin interface**: Painel administrativo pronto para gerenciar usuários
- **Session management**: Gerenciamento seguro de sessões
- **Password reset**: Funcionalidade de recuperação de senha out-of-the-box

Ao utilizar o Django, evitamos a necessidade de implementar ou integrar bibliotecas de autenticação de terceiros, reduzindo significativamente o tempo de desenvolvimento e potenciais vulnerabilidades de segurança.

## Consequências

### Positivas
- Redução significativa do tempo de desenvolvimento relacionado à autenticação
- Sistema de autenticação battle-tested e mantido pela comunidade
- Segurança aprimorada com práticas recomendadas já implementadas
- Facilidade para implementar autorização baseada em permissões
- Documentação extensa e comunidade ativa

### Negativas
- Framework full-stack pode ser considerado pesado para APIs puras
- Curva de aprendizado para desenvolvedores não familiarizados com Django
- Convenções opinionated do Django podem limitar algumas escolhas arquiteturais

## Alternativas Consideradas
- **FastAPI**: Framework mais leve, mas requer integração manual de sistema de autenticação
- **Flask**: Minimalista e flexível, mas necessita de extensões adicionais para autenticação completa
