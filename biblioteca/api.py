from django.db import connection
from django.db.utils import OperationalError
from ninja import NinjaAPI


from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from ninja.errors import HttpError
from biblioteca.schemas import UserCreateSchema, UserOutSchema, HealthCheckResponse

User = get_user_model()
api = NinjaAPI(
    title="Biblioteca API",
    version="1.0.0",
    description="API do Sistema de Gerenciamento de Biblioteca"
)


@api.post("/auth/register", response={201: UserOutSchema}, auth=None)
def register(request, payload: UserCreateSchema):
    if payload.email and User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Nome de usuário ou e-mail já está em uso.")
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=payload.username,
                email=payload.email,
                password=payload.password,
            )
            return 201, user
    except IntegrityError:
        raise HttpError(400, "Nome de usuário ou e-mail já está em uso.")


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
