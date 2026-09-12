"""Unit tests for authentication and security middleware.
"""

import json
from flask.testing import FlaskClient


def test_auth_obrigatoria_com_chave_invalida(client: FlaskClient):
    """Test 401 Unauthorized response when API_AUTH_KEY is enabled and no key is sent."""
    response = client.post(
        '/api/v1/treino',
        data=json.dumps({"objetivo": "Treino de braço"}),
        headers={'Content-Type': 'application/json'}
    )

    assert response.status_code == 401
    data = json.loads(response.data.decode('utf-8'))
    assert 'erro' in data
    assert 'não autorizado' in data['erro'].lower()


def test_auth_obrigatoria_com_chave_valida(client: FlaskClient, auth_headers: dict, mock_gemini):
    """Test successful access when supplying valid X-API-KEY header."""
    response = client.post(
        '/api/v1/treino',
        data=json.dumps({"objetivo": "Treino de braço", "nivel": "iniciante"}),
        headers=auth_headers
    )

    assert response.status_code == 201
