from datetime import datetime
from typing import Optional
from ninja import Schema
from pydantic import Field


class RentCreateSchema(Schema):
    physical_book_id: Optional[int] = Field(
        default=None,
        description="ID do exemplar físico a ser alugado.",
    )
    book_id: Optional[int] = Field(
        default=None,
        description="ID do livro (caso queira alugar automaticamente qualquer exemplar disponível).",
    )
    user_id: Optional[int] = Field(
        default=None,
        description="ID do usuário para quem o livro será alugado (opcional se autenticado).",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Data prevista de devolução. Se omitida, assume 14 dias a partir do empréstimo.",
    )


class RentOutSchema(Schema):
    id: int
    physical_book_id: int
    book_title: str
    user_id: int
    rented_at: datetime
    due_date: datetime
    returned_at: Optional[datetime] = None
    is_active: bool

    @staticmethod
    def resolve_book_title(obj) -> str:
        return obj.physical_book.book.title


class AvailableBookSchema(Schema):
    id: int
    title: str
    author_name: str
    available_copies: int

    @staticmethod
    def resolve_author_name(obj) -> str:
        return obj.author.name

    @staticmethod
    def resolve_available_copies(obj) -> int:
        return len(obj.available_copies_list)
