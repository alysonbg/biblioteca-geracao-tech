import json
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class HealthCheckTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint_exists(self):
        """Testa se o endpoint de healthcheck existe"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)

    def test_health_check_response_structure(self):
        """Testa se a resposta tem a estrutura esperada"""
        response = self.client.get('/api/health')
        data = response.json()

        self.assertIn('status', data)
        self.assertIn('database', data)
        self.assertIn('version', data)

    def test_health_check_database_connected(self):
        """Testa se o banco de dados está conectado"""
        response = self.client.get('/api/health')
        data = response.json()

        self.assertEqual(data['database'], 'connected')
        self.assertEqual(data['status'], 'healthy')

    def test_health_check_version(self):
        """Testa se a versão está presente"""
        response = self.client.get('/api/health')
        data = response.json()

        self.assertEqual(data['version'], '1.0.0')


class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = '/api/auth/register'
        self.valid_payload = {
            'username': 'novousuario',
            'email': 'novo@email.com',
            'password': 'senhaSegura123!',
        }

    def test_register_user_success(self):
        """Testa o registro bem-sucedido de um novo usuário."""
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()

        # Validação do payload de resposta
        self.assertIn('id', data)
        self.assertIsInstance(data['id'], int)
        self.assertEqual(data['username'], self.valid_payload['username'])
        self.assertEqual(data['email'], self.valid_payload['email'])
        self.assertNotIn('password', data)

        # Validação de persistência e segurança no banco de dados
        user = User.objects.filter(username=self.valid_payload['username']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.valid_payload['email'])
        self.assertTrue(user.check_password(self.valid_payload['password']))
        self.assertNotEqual(user.password, self.valid_payload['password'])

    def test_register_user_duplicate_username(self):
        """Testa a tentativa de registro com username duplicado."""
        User.objects.create_user(
            username=self.valid_payload['username'],
            email='outro@email.com',
            password='outrasenha123',
        )

        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('detail'), 'Nome de usuário ou e-mail já está em uso.')
        self.assertEqual(
            User.objects.filter(username=self.valid_payload['username']).count(),
            1,
        )

    def test_register_user_duplicate_email(self):
        """Testa a tentativa de registro com e-mail duplicado."""
        User.objects.create_user(
            username='usuarioexistente',
            email=self.valid_payload['email'],
            password='outrasenha123',
        )

        payload = {
            'username': 'novousuario2',
            'email': self.valid_payload['email'],
            'password': 'senhaSegura123!',
        }

        response = self.client.post(
            self.register_url,
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('detail'), 'Nome de usuário ou e-mail já está em uso.')
        self.assertFalse(User.objects.filter(username='novousuario2').exists())

    def test_register_user_missing_username(self):
        """Testa validação quando o campo 'username' está ausente no payload."""
        payload = {
            'email': 'novo@email.com',
            'password': 'senhaSegura123!',
        }

        response = self.client.post(
            self.register_url,
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 422)
        self.assertFalse(User.objects.filter(email='novo@email.com').exists())

    def test_register_user_missing_email(self):
        """Testa validação quando o campo 'email' está ausente no payload."""
        payload = {
            'username': 'novousuario',
            'password': 'senhaSegura123!',
        }

        response = self.client.post(
            self.register_url,
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 422)
        self.assertFalse(User.objects.filter(username='novousuario').exists())

    def test_register_user_missing_password(self):
        """Testa validação quando o campo 'password' está ausente no payload."""
        payload = {
            'username': 'novousuario',
            'email': 'novo@email.com',
        }

        response = self.client.post(
            self.register_url,
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 422)
        self.assertFalse(User.objects.filter(username='novousuario').exists())

    def test_register_user_empty_payload(self):
        """Testa validação quando o payload enviado é vazio."""
        response = self.client.post(
            self.register_url,
            data=json.dumps({}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 422)

    def test_register_user_invalid_json(self):
        """Testa requisição com corpo JSON malformado."""
        response = self.client.post(
            self.register_url,
            data='{invalid_json}',
            content_type='application/json',
        )

        self.assertIn(response.status_code, [400, 422])

    def test_register_user_methods_not_allowed(self):
        """Testa se outros métodos HTTP (GET, PUT, DELETE, PATCH) são rejeitados com 405."""
        disallowed_methods = [
            self.client.get,
            self.client.put,
            self.client.delete,
            self.client.patch,
        ]

        for method in disallowed_methods:
            with self.subTest(method=method.__name__):
                response = method(self.register_url)
                self.assertEqual(response.status_code, 405)

    def test_register_multiple_users_successfully(self):
        """Testa o registro de múltiplos usuários independentes com sucesso."""
        users_to_create = [
            {'username': 'user_one', 'email': 'user_one@test.com', 'password': 'pass_one_123'},
            {'username': 'user_two', 'email': 'user_two@test.com', 'password': 'pass_two_123'},
            {'username': 'user_three', 'email': 'user_three@test.com', 'password': 'pass_three_123'},
        ]

        created_ids = set()

        for user_data in users_to_create:
            response = self.client.post(
                self.register_url,
                data=json.dumps(user_data),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.assertEqual(data['username'], user_data['username'])
            self.assertEqual(data['email'], user_data['email'])
            self.assertNotIn(data['id'], created_ids)
            created_ids.add(data['id'])

        self.assertEqual(len(created_ids), 3)
        self.assertEqual(User.objects.filter(id__in=created_ids).count(), 3)
