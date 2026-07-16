import unittest
import json
from api_academia import create_app
from api_academia.config import Config
from api_academia.database import db
from api_academia.models import Treino

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Disable rate limiting for unit tests
    RATELIMIT_ENABLED = False

class APITestCase(unittest.TestCase):
    def setUp(self):
        # Instantiate a separate app instance with the test configuration
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        
        # Configure headers with API key if authentication is enabled
        self.headers = {'Content-Type': 'application/json'}
        auth_key = self.app.config.get('API_AUTH_KEY')
        if auth_key and auth_key.strip():
            self.headers['X-API-KEY'] = auth_key
        
        # Push application context and create all tables
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'operante')

    def test_criar_e_listar_treino(self):
        """Test generating a workout via Gemini and retrieving it from DB."""
        payload = {
            "objetivo": "Foco em pernas e glúteos",
            "nivel": "iniciante"
        }
        
        print("\n[TEST] Enviando requisição para gerar treino via Gemini...")
        response = self.client.post(
            '/api/v1/treino',
            data=json.dumps(payload),
            headers=self.headers
        )
        
        # Assert status code is 201 Created
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        
        # Verify returned structure
        self.assertIn('id', data)
        self.assertEqual(data['objetivo'], payload['objetivo'])
        self.assertEqual(data['nivel'], payload['nivel'])
        self.assertIn('treino_gerado', data)
        self.assertIn('criado_em', data)
        
        print(f"[TEST] Treino gerado com sucesso! ID: {data['id']}")
        print(f"[TEST] Treino:\n{data['treino_gerado']}\n")

        # Verify that it is persisted in the database by listing workouts
        response_list = self.client.get('/api/v1/treinos', headers=self.headers)
        self.assertEqual(response_list.status_code, 200)
        list_data = json.loads(response_list.data.decode('utf-8'))
        self.assertEqual(len(list_data), 1)
        self.assertEqual(list_data[0]['id'], data['id'])

if __name__ == '__main__':
    unittest.main()
