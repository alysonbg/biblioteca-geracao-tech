from django.conf import settings
from django.db import models
from django.utils import timezone


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        db_table = "authors"
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Título")
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="Autor",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        db_table = "books"
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title} ({self.author.name})"


class PhysicalBook(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Disponível"
        LOANED = "loaned", "Emprestado"
        MAINTENANCE = "maintenance", "Em Manutenção"
        LOST = "lost", "Extraviado"

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="physical_books",
        verbose_name="Livro",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        verbose_name="Status",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        db_table = "physical_books"
        verbose_name = "Exemplar Físico"
        verbose_name_plural = "Exemplares Físicos"
        ordering = ["book", "id"]

    def __str__(self) -> str:
        return f"{self.book.title} (Exemplar #{self.id} - {self.get_status_display()})"

    @property
    def is_available(self) -> bool:
        return self.status == self.Status.AVAILABLE


class Rent(models.Model):
    physical_book = models.ForeignKey(
        PhysicalBook,
        on_delete=models.PROTECT,
        related_name="rents",
        verbose_name="Exemplar Físico",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rents",
        verbose_name="Usuário",
    )
    rented_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Retirada",
    )
    due_date = models.DateTimeField(
        verbose_name="Data Prevista de Devolução",
    )
    returned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data Real de Devolução",
    )

    class Meta:
        db_table = "rents"
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"
        ordering = ["-rented_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["physical_book"],
                condition=models.Q(returned_at__isnull=True),
                name="unique_active_rent_per_book",
            )
        ]

    def __str__(self) -> str:
        return f"Empréstimo #{self.id} - {self.physical_book.book.title} ({self.user})"

    @property
    def is_active(self) -> bool:
        return self.returned_at is None
