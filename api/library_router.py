from ninja import Router
from ninja.errors import HttpError
from ninja.security import django_auth
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth

from api.models import Rent
from api.schemas import RentCreateSchema, RentOutSchema
from api.services import RentService

library_router = Router(tags=["Empréstimos"])
router = library_router  # alias para conveniência


@library_router.post(
    "/rents/",
    response={201: RentOutSchema},
    auth=[HttpJwtAuth(), django_auth],
    summary="Aluga um exemplar de livro",
    description="Registra o empréstimo de um livro físico para o usuário autenticado ou especificado via user_id.",
)
def create_rent(request, payload: RentCreateSchema):
    """Cria um novo empréstimo de exemplar físico."""
    rent = RentService.rent_book(
        user=request.user,
        user_id=payload.user_id,
        physical_book_id=payload.physical_book_id,
        book_id=payload.book_id,
        due_date=payload.due_date,
    )
    return 201, rent


@library_router.get(
    "/rents/",
    response=list[RentOutSchema],
    auth=[HttpJwtAuth(), django_auth],
    summary="Lista empréstimos",
    description="Lista os empréstimos cadastrados. Usuários comuns veem seus próprios; equipe vê todos.",
)
def list_rents(request, active_only: bool = False):
    """Lista os empréstimos com filtro opcional de empréstimos ativos."""
    queryset = Rent.objects.select_related("physical_book__book", "user").all()

    if not getattr(request.user, "is_staff", False):
        queryset = queryset.filter(user=request.user)

    if active_only:
        queryset = queryset.filter(returned_at__isnull=True)

    return list(queryset)


@library_router.get(
    "/rents/{int:rent_id}/",
    response=RentOutSchema,
    auth=[HttpJwtAuth(), django_auth],
    summary="Detalhes de um empréstimo",
)
def get_rent(request, rent_id: int):
    """Obtém detalhes de um empréstimo específico."""
    queryset = Rent.objects.select_related("physical_book__book", "user")
    if not getattr(request.user, "is_staff", False):
        queryset = queryset.filter(user=request.user)

    rent = queryset.filter(id=rent_id).first()
    if not rent:
        raise HttpError(404, "Empréstimo não encontrado.")

    return rent


@library_router.post(
    "/rents/{int:rent_id}/return/",
    response=RentOutSchema,
    auth=[HttpJwtAuth(), django_auth],
    summary="Devolve um livro alugado",
    description="Finaliza o empréstimo e marca o exemplar físico como disponível.",
)
def return_rent(request, rent_id: int):
    """Registra a devolução do livro alugado."""
    return RentService.return_book(rent_id=rent_id, user=request.user)
