"""Tests for the optional user profile fields sent by the HIPERTROF.IA backend.
"""

import json
from flask.testing import FlaskClient

from api_academia.services import generate_treino


PERFIL_COMPLETO = {
    "objetivo": "hipertrofia",
    "nivel": "intermediario",
    "altura": 180,
    "peso": 80.5,
    "idade": 25,
    "vezes_por_semana": 4,
    "tempo": 60,
}


def test_criar_treino_com_perfil_completo(client: FlaskClient, auth_headers: dict, mock_gemini):
    """The full profile is accepted and forwarded to the AI service."""
    response = client.post('/api/v1/treino', data=json.dumps(PERFIL_COMPLETO), headers=auth_headers)

    assert response.status_code == 201
    mock_gemini.assert_called_once_with(
        objetivo="hipertrofia",
        nivel="intermediario",
        perfil={"altura": 180, "peso": 80.5, "idade": 25, "vezes_por_semana": 4, "tempo": 60},
    )


def test_criar_treino_perfil_fora_dos_limites(client: FlaskClient, auth_headers: dict, mock_gemini):
    """Out-of-range profile values are rejected before calling the AI."""
    payload = {**PERFIL_COMPLETO, "idade": -1, "vezes_por_semana": 9}
    response = client.post('/api/v1/treino', data=json.dumps(payload), headers=auth_headers)

    assert response.status_code == 400
    erros = json.loads(response.data.decode('utf-8'))['erros_validacao']
    assert 'idade' in erros and 'vezes_por_semana' in erros
    mock_gemini.assert_not_called()


def test_campo_desconhecido_continua_rejeitado(client: FlaskClient, auth_headers: dict, mock_gemini):
    """Unknown fields are still rejected (strict input validation)."""
    payload = {**PERFIL_COMPLETO, "senha": "x"}
    response = client.post('/api/v1/treino', data=json.dumps(payload), headers=auth_headers)

    assert response.status_code == 400
    mock_gemini.assert_not_called()


def test_prompt_inclui_perfil(app, mocker):
    """The Gemini prompt mentions every profile field provided."""
    fake_client = mocker.patch('api_academia.services.genai.Client')
    fake_client.return_value.models.generate_content.return_value.text = "Treino A"

    generate_treino(
        objetivo="hipertrofia",
        nivel="iniciante",
        perfil={"altura": 180, "peso": 80, "idade": 25, "vezes_por_semana": 3, "tempo": 45},
    )

    prompt = fake_client.return_value.models.generate_content.call_args.kwargs['contents']
    for trecho in ("180", "80", "25 anos", "3 vezes por semana", "45 minutos"):
        assert trecho in prompt
    assert "exatamente 3 treinos" in prompt
    assert "'Treino A: <grupos musculares>'" in prompt
