from django.db import connection
from django.db.utils import OperationalError
from ninja import NinjaAPI, Schema

api = NinjaAPI(
    title="Biblioteca API",
    version="1.0.0",
    description="API do Sistema de Gerenciamento de Biblioteca"
)


class HealthCheckResponse(Schema):
    status: str
    database: str
    version: str


@api.get("/health", response=HealthCheckResponse, tags=["Health"])
def health_check(request):
    """
    Endpoint de healthcheck para verificar o status da aplicação.

    Retorna:
    - status: "healthy" se tudo estiver funcionando
    - database: "connected" se o banco estiver acessível
    - version: versão da aplicação
    """
    # Verifica conexão com o banco de dados
    try:
        connection.ensure_connection()
        db_status = "connected"
    except OperationalError:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "version": "1.0.0"
    }
