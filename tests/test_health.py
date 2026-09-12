"""Unit and integration tests for application health check and root landing routes.
"""

import json
from flask.testing import FlaskClient


def test_root_home(client: FlaskClient):
    """Test root '/' landing endpoint returns HTTP 200 with JSON metadata."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'online'
    assert 'endpoints' in data


def test_api_health_check(client: FlaskClient):
    """Test '/api/v1/health' endpoint returns HTTP 200 and operational status."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'operante'
    assert 'mensagem' in data
