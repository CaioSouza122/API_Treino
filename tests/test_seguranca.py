"""Security regression tests: fail-closed auth, no leaked internals, bounded listing, CORS.
"""

import json

import pytest
from flask.testing import FlaskClient

from api_academia import create_app
from tests.conftest import TestConfig


class ProducaoSemChave(TestConfig):
    TESTING = False
    DEBUG = False
    API_AUTH_KEY = ""


def test_producao_sem_chave_nao_inicia():
    """Outside debug/testing the app refuses to start without API_AUTH_KEY."""
    with pytest.raises(RuntimeError, match="API_AUTH_KEY"):
        create_app(ProducaoSemChave)


def test_chave_errada_retorna_401(client: FlaskClient):
    headers = {'Content-Type': 'application/json', 'X-API-KEY': 'chave-errada'}
    response = client.get('/api/v1/treinos', headers=headers)
    assert response.status_code == 401


def test_erro_interno_nao_vaza_detalhes(client: FlaskClient, auth_headers: dict, mocker):
    """Exception text (hosts, queries) stays in the log, never in the response."""
    mocker.patch('api_academia.routes.generate_treino', side_effect=Exception("host=db.neon.tech senha=xyz"))
    response = client.post(
        '/api/v1/treino', data=json.dumps({"objetivo": "hipertrofia"}), headers=auth_headers
    )
    assert response.status_code == 500
    corpo = response.data.decode('utf-8')
    assert "neon" not in corpo and "senha" not in corpo


def test_listagem_respeita_limite(client: FlaskClient, auth_headers: dict, mock_gemini):
    for _ in range(3):
        client.post('/api/v1/treino', data=json.dumps({"objetivo": "hipertrofia"}), headers=auth_headers)
    response = client.get('/api/v1/treinos?limit=2', headers=auth_headers)
    assert response.status_code == 200
    assert len(json.loads(response.data.decode('utf-8'))) == 2


def test_cors_desligado_por_padrao(client: FlaskClient):
    """Server-to-server API: browsers get no CORS headers unless ALLOWED_ORIGINS is set."""
    response = client.get('/api/v1/health', headers={'Origin': 'https://site-qualquer.com'})
    assert 'Access-Control-Allow-Origin' not in response.headers


def test_limite_conta_por_chave_e_nao_por_ip(app):
    """Requests with an API key share a bucket per key, not per proxy IP."""
    from api_academia.limiter import client_key

    with app.test_request_context(headers={'X-API-KEY': 'a'}, environ_base={'REMOTE_ADDR': '10.0.0.1'}):
        chave_a = client_key()
    with app.test_request_context(headers={'X-API-KEY': 'b'}, environ_base={'REMOTE_ADDR': '10.0.0.1'}):
        chave_b = client_key()
    assert chave_a != chave_b and chave_a.startswith("key:")
