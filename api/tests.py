from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase

from api.admin import AuthorAdmin, BookAdmin, PhysicalBookAdmin, RentAdmin
from api.models import Author, Book, PhysicalBook, Rent


class AdminRegistrationTestCase(SimpleTestCase):
    def test_author_registered_in_admin(self):
        """Testa se o modelo Author foi registrado no admin com a classe esperada."""
        self.assertIn(Author, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Author], AuthorAdmin)

    def test_book_registered_in_admin(self):
        """Testa se o modelo Book foi registrado no admin com a classe esperada."""
        self.assertIn(Book, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Book], BookAdmin)

    def test_physical_book_registered_in_admin(self):
        """Testa se o modelo PhysicalBook foi registrado no admin com a classe esperada."""
        self.assertIn(PhysicalBook, admin.site._registry)
        self.assertIsInstance(admin.site._registry[PhysicalBook], PhysicalBookAdmin)

    def test_rent_registered_in_admin(self):
        """Testa se o modelo Rent foi registrado no admin com a classe esperada."""
        self.assertIn(Rent, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Rent], RentAdmin)

    def test_author_admin_attributes(self):
        """Testa as configurações de AuthorAdmin."""
        author_admin = admin.site._registry[Author]
        self.assertEqual(author_admin.list_display, ("id", "name", "created_at"))
        self.assertEqual(author_admin.search_fields, ("name",))
        self.assertEqual(author_admin.list_filter, ("created_at",))
        self.assertEqual(author_admin.readonly_fields, ("created_at",))

    def test_book_admin_attributes(self):
        """Testa as configurações de BookAdmin."""
        book_admin = admin.site._registry[Book]
        self.assertEqual(book_admin.list_display, ("id", "title", "author", "created_at"))
        self.assertEqual(book_admin.search_fields, ("title", "author__name"))
        self.assertEqual(book_admin.list_filter, ("author", "created_at"))
        self.assertEqual(book_admin.autocomplete_fields, ("author",))
        self.assertEqual(book_admin.readonly_fields, ("created_at",))

    def test_physical_book_admin_attributes(self):
        """Testa as configurações de PhysicalBookAdmin."""
        pb_admin = admin.site._registry[PhysicalBook]
        self.assertEqual(pb_admin.list_display, ("id", "book", "status", "created_at"))
        self.assertEqual(pb_admin.search_fields, ("book__title",))
        self.assertEqual(pb_admin.list_filter, ("status", "created_at"))
        self.assertEqual(pb_admin.autocomplete_fields, ("book",))
        self.assertEqual(pb_admin.readonly_fields, ("created_at",))

    def test_rent_admin_attributes(self):
        """Testa as configurações de RentAdmin."""
        rent_admin = admin.site._registry[Rent]
        self.assertEqual(
            rent_admin.list_display,
            (
                "id",
                "physical_book",
                "user",
                "rented_at",
                "due_date",
                "returned_at",
                "is_active",
            ),
        )
        self.assertEqual(
            rent_admin.search_fields,
            ("physical_book__book__title", "user__username", "user__email"),
        )
        self.assertEqual(rent_admin.list_filter, ("rented_at", "due_date", "returned_at"))
        self.assertEqual(rent_admin.autocomplete_fields, ("physical_book", "user"))


class ModelsTestCase(SimpleTestCase):
    def test_author_str(self):
        """Testa a representação em string do modelo Author."""
        author = Author(name="Machado de Assis")
        self.assertEqual(str(author), "Machado de Assis")

    def test_book_str(self):
        """Testa a representação em string do modelo Book."""
        author = Author(name="Machado de Assis")
        book = Book(title="Dom Casmurro", author=author)
        self.assertEqual(str(book), "Dom Casmurro (Machado de Assis)")

    def test_physical_book_str_and_availability(self):
        """Testa a representação em string e a propriedade is_available de PhysicalBook."""
        author = Author(name="Machado de Assis")
        book = Book(title="Dom Casmurro", author=author)
        pb = PhysicalBook(id=1, book=book, status=PhysicalBook.Status.AVAILABLE)
        self.assertEqual(str(pb), "Dom Casmurro (Exemplar #1 - Disponível)")
        self.assertTrue(pb.is_available)

        pb.status = PhysicalBook.Status.LOANED
        self.assertFalse(pb.is_available)

    def test_rent_str_and_is_active(self):
        """Testa a representação em string e a propriedade is_active de Rent."""
        user_model = get_user_model()
        user = user_model(username="alyson")
        author = Author(name="Machado de Assis")
        book = Book(title="Dom Casmurro", author=author)
        pb = PhysicalBook(id=1, book=book)
        rent = Rent(id=10, physical_book=pb, user=user)
        self.assertEqual(str(rent), "Empréstimo #10 - Dom Casmurro (alyson)")
        self.assertTrue(rent.is_active)
