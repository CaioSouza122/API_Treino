"""Integration tests for workout CRUD endpoints (/api/v1/treino and /api/v1/treinos).
"""

import json
from flask.testing import FlaskClient


def test_criar_treino_sucesso(client: FlaskClient, auth_headers: dict, mock_gemini):
    """Test generating a workout via AI service and persisting to database."""
    payload = {
        "objetivo": "Ganho de massa muscular em membros inferiores",
        "nivel": "intermediario"
    }

    response = client.post(
        '/api/v1/treino',
        data=json.dumps(payload),
        headers=auth_headers
    )

    assert response.status_code == 201
    data = json.loads(response.data.decode('utf-8'))

    assert 'id' in data
    assert data['objetivo'] == payload['objetivo']
    assert data['nivel'] == payload['nivel']
    assert "Agachamento Livre" in data['treino_gerado']
    assert 'criado_em' in data

    # Verify mock service was called with correct parameters
    mock_gemini.assert_called_once_with(objetivo=payload['objetivo'], nivel=payload['nivel'], perfil={})


def test_criar_treino_payload_invalido(client: FlaskClient, auth_headers: dict):
    """Test validation errors when sending invalid or missing fields."""
    payload = {
        "objetivo": "ab",  # Too short (min 3 chars required)
        "nivel": "expert"  # Invalid level
    }

    response = client.post(
        '/api/v1/treino',
        data=json.dumps(payload),
        headers=auth_headers
    )

    assert response.status_code == 400
    data = json.loads(response.data.decode('utf-8'))
    assert 'erros_validacao' in data


def test_listar_e_obter_treino_por_id(client: FlaskClient, auth_headers: dict, mock_gemini):
    """Test creating, listing all, and obtaining a workout routine by ID."""
    # 1. Create a workout
    payload = {"objetivo": "Resistência cardiovascular", "nivel": "iniciante"}
    res_create = client.post('/api/v1/treino', data=json.dumps(payload), headers=auth_headers)
    assert res_create.status_code == 201
    treino_id = json.loads(res_create.data.decode('utf-8'))['id']

    # 2. List all workouts
    res_list = client.get('/api/v1/treinos', headers=auth_headers)
    assert res_list.status_code == 200
    list_data = json.loads(res_list.data.decode('utf-8'))
    assert len(list_data) == 1
    assert list_data[0]['id'] == treino_id

    # 3. Get workout by ID
    res_get = client.get(f'/api/v1/treino/{treino_id}', headers=auth_headers)
    assert res_get.status_code == 200
    get_data = json.loads(res_get.data.decode('utf-8'))
    assert get_data['id'] == treino_id
    assert get_data['objetivo'] == payload['objetivo']


def test_deletar_treino(client: FlaskClient, auth_headers: dict, mock_gemini):
    """Test deleting a workout routine by ID."""
    payload = {"objetivo": "Treino funcional para ombros", "nivel": "avancado"}
    res_create = client.post('/api/v1/treino', data=json.dumps(payload), headers=auth_headers)
    treino_id = json.loads(res_create.data.decode('utf-8'))['id']

    # Delete workout
    res_del = client.delete(f'/api/v1/treino/{treino_id}', headers=auth_headers)
    assert res_del.status_code == 200

    # Ensure workout no longer exists
    res_get = client.get(f'/api/v1/treino/{treino_id}', headers=auth_headers)
    assert res_get.status_code == 404
