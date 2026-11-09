from django.test import TestCase, Client


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
