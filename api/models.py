from django.db import models


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
