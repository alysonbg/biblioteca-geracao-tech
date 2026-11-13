from datetime import timedelta
import json

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.utils import timezone
from ninja.errors import HttpError
from ninja_simple_jwt.jwt.token_operations import get_access_token_for_user

from api.admin import AuthorAdmin, BookAdmin, PhysicalBookAdmin, RentAdmin
from api.models import Author, Book, PhysicalBook, Rent
from api.services import RentService

User = get_user_model()


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
        user = User(username="alyson")
        author = Author(name="Machado de Assis")
        book = Book(title="Dom Casmurro", author=author)
        pb = PhysicalBook(id=1, book=book)
        rent = Rent(id=10, physical_book=pb, user=user)
        self.assertEqual(str(rent), "Empréstimo #10 - Dom Casmurro (alyson)")
        self.assertTrue(rent.is_active)


class RentServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="leitor1",
            email="leitor1@biblioteca.com",
            password="senhaSegura123!",
        )
        self.author = Author.objects.create(name="Clarice Lispector")
        self.book = Book.objects.create(title="A Hora da Estrela", author=self.author)
        self.physical_book = PhysicalBook.objects.create(
            book=self.book,
            status=PhysicalBook.Status.AVAILABLE,
        )

    def test_rent_book_success_with_physical_book_id(self):
        """Testa empréstimo bem-sucedido informando o ID do exemplar físico."""
        rent = RentService.rent_book(
            user=self.user,
            physical_book_id=self.physical_book.id,
        )

        self.assertIsNotNone(rent.id)
        self.assertEqual(rent.user, self.user)
        self.assertEqual(rent.physical_book, self.physical_book)
        self.assertTrue(rent.is_active)
        self.assertIsNone(rent.returned_at)

        # Verifica transição de status no banco de dados
        self.physical_book.refresh_from_db()
        self.assertEqual(self.physical_book.status, PhysicalBook.Status.LOANED)

    def test_rent_book_success_with_book_id(self):
        """Testa empréstimo bem-sucedido selecionando automaticamente exemplar disponível."""
        rent = RentService.rent_book(
            user=self.user,
            book_id=self.book.id,
        )

        self.assertEqual(rent.physical_book, self.physical_book)
        self.physical_book.refresh_from_db()
        self.assertEqual(self.physical_book.status, PhysicalBook.Status.LOANED)

    def test_rent_book_custom_due_date(self):
        """Testa definição de data prevista de devolução personalizada no futuro."""
        future_date = timezone.now() + timedelta(days=30)
        rent = RentService.rent_book(
            user=self.user,
            physical_book_id=self.physical_book.id,
            due_date=future_date,
        )
        self.assertEqual(rent.due_date, future_date)

    def test_rent_book_with_explicit_user_id(self):
        """Testa empréstimo informando explicitamente user_id."""
        rent = RentService.rent_book(
            user_id=self.user.id,
            physical_book_id=self.physical_book.id,
        )
        self.assertEqual(rent.user, self.user)

    def test_rent_book_unauthenticated_without_user_id(self):
        """Testa erro 401 ao tentar alugar sem usuário autenticado e sem user_id."""
        with self.assertRaises(HttpError) as context:
            RentService.rent_book(physical_book_id=self.physical_book.id)
        self.assertEqual(context.exception.status_code, 401)

    def test_rent_book_nonexistent_user_id(self):
        """Testa erro 404 ao informar user_id que não existe."""
        with self.assertRaises(HttpError) as context:
            RentService.rent_book(
                user_id=999999,
                physical_book_id=self.physical_book.id,
            )
        self.assertEqual(context.exception.status_code, 404)

    def test_rent_book_past_due_date(self):
        """Testa erro 400 ao fornecer data de devolução no passado."""
        past_date = timezone.now() - timedelta(days=1)
        with self.assertRaises(HttpError) as context:
            RentService.rent_book(
                user=self.user,
                physical_book_id=self.physical_book.id,
                due_date=past_date,
            )
        self.assertEqual(context.exception.status_code, 400)

    def test_rent_book_nonexistent_physical_book(self):
        """Testa erro 404 ao tentar alugar exemplar físico inexistente."""
        with self.assertRaises(HttpError) as context:
            RentService.rent_book(
                user=self.user,
                physical_book_id=999999,
            )
        self.assertEqual(context.exception.status_code, 404)

    def test_rent_book_nonexistent_book(self):
        """Testa erro 404 ao tentar alugar livro inexistente."""
        with self.assertRaises(HttpError) as context:
            RentService.rent_book(
                user=self.user,
                book_id=999999,
            )
        self.assertEqual(context.exception.status_code, 404)

    def test_rent_book_physical_book_not_available(self):
        """Testa erro 400 quando o exemplar físico não está disponível."""
        invalid_statuses = [
            PhysicalBook.Status.LOANED,
            PhysicalBook.Status.MAINTENANCE,
            PhysicalBook.Status.LOST,
        ]
        for st in invalid_statuses:
            with self.subTest(status=st):
                self.physical_book.status = st
                self.physical_book.save(update_fields=["status"])
                with self.assertRaises(HttpError) as context:
                    RentService.rent_book(
                        user=self.user,
                        physical_book_id=self.physical_book.id,
                    )
                self.assertEqual(context.exception.status_code, 400)

    def test_rent_book_no_available_copies_for_book(self):
        """Testa erro 400 quando todas as cópias de um livro estão ocupadas."""
        self.physical_book.status = PhysicalBook.Status.LOANED
        self.physical_book.save(update_fields=["status"])

        with self.assertRaises(HttpError) as context:
            RentService.rent_book(
                user=self.user,
                book_id=self.book.id,
            )
        self.assertEqual(context.exception.status_code, 400)

    def test_rent_book_missing_both_identifiers(self):
        """Testa erro 400 ao omitir tanto physical_book_id quanto book_id."""
        with self.assertRaises(HttpError) as context:
            RentService.rent_book(user=self.user)
        self.assertEqual(context.exception.status_code, 400)

    def test_return_book_success(self):
        """Testa devolução bem-sucedida de exemplar físico."""
        rent = RentService.rent_book(
            user=self.user,
            physical_book_id=self.physical_book.id,
        )

        returned_rent = RentService.return_book(rent_id=rent.id, user=self.user)
        self.assertFalse(returned_rent.is_active)
        self.assertIsNotNone(returned_rent.returned_at)

        self.physical_book.refresh_from_db()
        self.assertEqual(self.physical_book.status, PhysicalBook.Status.AVAILABLE)

    def test_return_book_already_returned(self):
        """Testa erro 400 ao tentar devolver um empréstimo já finalizado."""
        rent = RentService.rent_book(
            user=self.user,
            physical_book_id=self.physical_book.id,
        )
        RentService.return_book(rent_id=rent.id, user=self.user)

        with self.assertRaises(HttpError) as context:
            RentService.return_book(rent_id=rent.id, user=self.user)
        self.assertEqual(context.exception.status_code, 400)

    def test_return_book_not_found(self):
        """Testa erro 404 ao tentar devolver empréstimo inexistente."""
        with self.assertRaises(HttpError) as context:
            RentService.return_book(rent_id=999999, user=self.user)
        self.assertEqual(context.exception.status_code, 404)

    def test_return_book_unauthorized_user(self):
        """Testa erro 403 quando outro usuário que não é staff tenta devolver o livro."""
        other_user = User.objects.create_user(
            username="outro",
            email="outro@biblioteca.com",
            password="senhaSegura123!",
        )
        rent = RentService.rent_book(
            user=self.user,
            physical_book_id=self.physical_book.id,
        )

        with self.assertRaises(HttpError) as context:
            RentService.return_book(rent_id=rent.id, user=other_user)
        self.assertEqual(context.exception.status_code, 403)


class RentAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="maria",
            email="maria@teste.com",
            password="senhaSegura123!",
        )
        self.other_user = User.objects.create_user(
            username="joao",
            email="joao@teste.com",
            password="senhaSegura123!",
        )
        self.staff_user = User.objects.create_user(
            username="admin_user",
            email="admin@teste.com",
            password="senhaSegura123!",
            is_staff=True,
        )

        token, _ = get_access_token_for_user(self.user)
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        staff_token, _ = get_access_token_for_user(self.staff_user)
        self.staff_auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {staff_token}"}

        self.author = Author.objects.create(name="Graciliano Ramos")
        self.book = Book.objects.create(title="Vidas Secas", author=self.author)
        self.physical_book = PhysicalBook.objects.create(
            book=self.book,
            status=PhysicalBook.Status.AVAILABLE,
        )
        self.rents_url = "/api/rents/"

    def test_rent_book_api_success_with_jwt(self):
        """Testa requisição de aluguel autenticada via JWT."""
        payload = {"physical_book_id": self.physical_book.id}
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()

        self.assertIn("id", data)
        self.assertEqual(data["physical_book_id"], self.physical_book.id)
        self.assertEqual(data["book_title"], self.book.title)
        self.assertEqual(data["user_id"], self.user.id)
        self.assertTrue(data["is_active"])
        self.assertIsNone(data["returned_at"])
        self.assertIn("rented_at", data)
        self.assertIn("due_date", data)

        self.physical_book.refresh_from_db()
        self.assertEqual(self.physical_book.status, PhysicalBook.Status.LOANED)

    def test_rent_book_api_success_with_book_id(self):
        """Testa aluguel automático de exemplar informando book_id."""
        payload = {"book_id": self.book.id}
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["physical_book_id"], self.physical_book.id)

    def test_rent_book_api_with_custom_due_date(self):
        """Testa envio de data de devolução personalizada."""
        custom_date = (timezone.now() + timedelta(days=20)).isoformat()
        payload = {
            "physical_book_id": self.physical_book.id,
            "due_date": custom_date,
        }
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 201)

    def test_rent_book_api_staff_rents_for_other_user(self):
        """Testa locação especificando user_id de outro usuário."""
        payload = {
            "physical_book_id": self.physical_book.id,
            "user_id": self.other_user.id,
        }
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.staff_auth_headers,
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["user_id"], self.other_user.id)

    def test_rent_book_api_unauthenticated(self):
        """Testa rejeição 401 para requisições não autenticadas."""
        payload = {"physical_book_id": self.physical_book.id}
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_rent_book_api_invalid_token(self):
        """Testa rejeição 401 com token JWT inválido."""
        payload = {"physical_book_id": self.physical_book.id}
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer token_invalido",
        )
        self.assertEqual(response.status_code, 401)

    def test_rent_book_api_physical_book_not_found(self):
        """Testa retorno 404 para physical_book_id inexistente."""
        payload = {"physical_book_id": 999999}
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_rent_book_api_book_not_found(self):
        """Testa retorno 404 para book_id inexistente."""
        payload = {"book_id": 999999}
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_rent_book_api_already_loaned(self):
        """Testa retorno 400 ao tentar alugar exemplar já emprestado."""
        self.physical_book.status = PhysicalBook.Status.LOANED
        self.physical_book.save(update_fields=["status"])

        payload = {"physical_book_id": self.physical_book.id}
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_rent_book_api_past_due_date(self):
        """Testa retorno 400 para data no passado."""
        past_date = (timezone.now() - timedelta(days=2)).isoformat()
        payload = {
            "physical_book_id": self.physical_book.id,
            "due_date": past_date,
        }
        response = self.client.post(
            self.rents_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_rent_book_api_empty_payload(self):
        """Testa retorno 400 ao enviar payload sem identificadores."""
        response = self.client.post(
            self.rents_url,
            data=json.dumps({}),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_list_rents_endpoint(self):
        """Testa listagem de empréstimos (usuário comum vê os seus)."""
        rent = RentService.rent_book(
            user=self.user,
            physical_book_id=self.physical_book.id,
        )

        response = self.client.get(self.rents_url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], rent.id)

    def test_get_rent_by_id_endpoint(self):
        """Testa busca de empréstimo por ID."""
        rent = RentService.rent_book(
            user=self.user,
            physical_book_id=self.physical_book.id,
        )

        response = self.client.get(f"{self.rents_url}{rent.id}/", **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], rent.id)

    def test_get_rent_by_id_not_found(self):
        """Testa erro 404 ao buscar empréstimo inexistente."""
        response = self.client.get(f"{self.rents_url}999999/", **self.auth_headers)
        self.assertEqual(response.status_code, 404)

    def test_return_rent_endpoint_success(self):
        """Testa devolução via endpoint POST /rents/{id}/return/."""
        rent = RentService.rent_book(
            user=self.user,
            physical_book_id=self.physical_book.id,
        )

        response = self.client.post(
            f"{self.rents_url}{rent.id}/return/",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_active"])
        self.assertIsNotNone(data["returned_at"])

        self.physical_book.refresh_from_db()
        self.assertEqual(self.physical_book.status, PhysicalBook.Status.AVAILABLE)
