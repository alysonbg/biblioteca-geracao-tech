from datetime import datetime, timedelta
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from ninja.errors import HttpError

from api.models import Book, PhysicalBook, Rent

User = get_user_model()


class RentService:
    """Serviço responsável por concentrar as regras de negócio de empréstimos de livros."""

    DEFAULT_RENT_DAYS = 14

    @classmethod
    def rent_book(
        cls,
        user: Optional[User] = None,
        user_id: Optional[int] = None,
        physical_book_id: Optional[int] = None,
        book_id: Optional[int] = None,
        due_date: Optional[datetime] = None,
    ) -> Rent:
        """
        Realiza o aluguel de um exemplar físico para um usuário.

        Regras:
        1. O usuário é obtido da sessão/JWT ou explicitamente via user_id.
        2. A data de devolução prevista deve ser no futuro; se omitida, assume 14 dias.
        3. O exemplar deve existir e estar com status 'available'.
        4. Transição atômica do status do exemplar para 'loaned' e criação do registro de Rent.
        """
        target_user = cls._resolve_user(user=user, user_id=user_id)
        validated_due_date = cls._validate_due_date(due_date=due_date)

        with transaction.atomic():
            physical_book = cls._acquire_physical_book(
                physical_book_id=physical_book_id,
                book_id=book_id,
            )

            # Validação defensiva de concorrência contra múltiplos empréstimos ativos
            if Rent.objects.filter(physical_book=physical_book, returned_at__isnull=True).exists():
                raise HttpError(400, "Este exemplar físico já possui um empréstimo ativo.")

            physical_book.status = PhysicalBook.Status.LOANED
            physical_book.save(update_fields=["status"])

            try:
                rent = Rent.objects.create(
                    physical_book=physical_book,
                    user=target_user,
                    rented_at=timezone.now(),
                    due_date=validated_due_date,
                )
            except IntegrityError:
                raise HttpError(400, "Este exemplar físico já possui um empréstimo ativo.")

            return rent

    @classmethod
    def return_book(cls, rent_id: int, user: Optional[User] = None) -> Rent:
        """
        Realiza a devolução de um exemplar alugado.

        Regras:
        1. O empréstimo deve existir e estar ativo (returned_at é nulo).
        2. O usuário autenticado deve ser o dono do empréstimo ou membro da equipe (staff).
        3. O exemplar físico volta ao status 'available' e a data de devolução é registrada.
        """
        with transaction.atomic():
            rent = (
                Rent.objects.select_for_update()
                .select_related("physical_book", "user")
                .filter(id=rent_id)
                .first()
            )

            if not rent:
                raise HttpError(404, "Empréstimo não encontrado.")

            if not rent.is_active:
                raise HttpError(400, "Este empréstimo já foi finalizado.")

            if user and not getattr(user, "is_staff", False) and rent.user_id != user.id:
                raise HttpError(403, "Você não tem permissão para devolver este empréstimo.")

            rent.returned_at = timezone.now()
            rent.save(update_fields=["returned_at"])

            rent.physical_book.status = PhysicalBook.Status.AVAILABLE
            rent.physical_book.save(update_fields=["status"])

            return rent

    @classmethod
    def _resolve_user(cls, user: Optional[User], user_id: Optional[int]) -> User:
        """Resolve o usuário alvo da locação."""
        if user_id is not None:
            found_user = User.objects.filter(id=user_id).first()
            if not found_user:
                raise HttpError(404, "Usuário informado não foi encontrado.")
            return found_user

        if user is not None and getattr(user, "is_authenticated", False):
            return user

        raise HttpError(401, "Autenticação obrigatória para realizar o empréstimo.")

    @classmethod
    def _validate_due_date(cls, due_date: Optional[datetime]) -> datetime:
        """Valida e retorna a data de devolução prevista."""
        now = timezone.now()
        if due_date is None:
            return now + timedelta(days=cls.DEFAULT_RENT_DAYS)

        if due_date <= now:
            raise HttpError(400, "A data prevista de devolução deve ser no futuro.")

        return due_date

    @classmethod
    def _acquire_physical_book(
        cls,
        physical_book_id: Optional[int],
        book_id: Optional[int],
    ) -> PhysicalBook:
        """Localiza e bloqueia com select_for_update o exemplar disponível."""
        if physical_book_id is None and book_id is None:
            raise HttpError(400, "É obrigatório informar 'physical_book_id' ou 'book_id'.")

        if physical_book_id is not None:
            physical_book = (
                PhysicalBook.objects.select_for_update()
                .select_related("book")
                .filter(id=physical_book_id)
                .first()
            )
            if not physical_book:
                raise HttpError(404, "Exemplar físico não encontrado.")

            if physical_book.status != PhysicalBook.Status.AVAILABLE:
                status_display = physical_book.get_status_display()
                raise HttpError(
                    400,
                    f"Exemplar físico não está disponível para empréstimo. Status atual: {status_display}."
                )

            return physical_book

        book = Book.objects.filter(id=book_id).first()
        if not book:
            raise HttpError(404, "Livro não encontrado.")

        physical_book = (
            PhysicalBook.objects.select_for_update()
            .select_related("book")
            .filter(book=book, status=PhysicalBook.Status.AVAILABLE)
            .first()
        )
        if not physical_book:
            raise HttpError(400, "Não há exemplares físicos disponíveis para este livro no momento.")

        return physical_book
