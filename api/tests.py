from django.contrib import admin
from django.test import SimpleTestCase

from api.admin import AuthorAdmin, BookAdmin
from api.models import Author, Book


class AdminRegistrationTestCase(SimpleTestCase):
    def test_author_registered_in_admin(self):
        """Testa se o modelo Author foi registrado no admin com a classe esperada."""
        self.assertIn(Author, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Author], AuthorAdmin)

    def test_book_registered_in_admin(self):
        """Testa se o modelo Book foi registrado no admin com a classe esperada."""
        self.assertIn(Book, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Book], BookAdmin)

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
