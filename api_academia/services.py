"""Service layer handling AI integrations and business logic.

This module isolates calls to the official Google GenAI SDK (Gemini 2.5 Flash),
ensuring clean separation of concerns from HTTP controllers and routes.
"""

import time
from typing import Any, Dict, Optional

from flask import current_app
from google import genai


def _descrever_perfil(perfil: Dict[str, Any]) -> str:
    """Turns the optional user profile into a sentence for the AI prompt."""
    partes = []
    if 'idade' in perfil:
        partes.append(f"{perfil['idade']} anos")
    if 'altura' in perfil:
        partes.append(f"altura {perfil['altura']:g}")
    if 'peso' in perfil:
        partes.append(f"peso {perfil['peso']:g} kg")
    if 'vezes_por_semana' in perfil:
        partes.append(f"treina {perfil['vezes_por_semana']} vezes por semana")
    if 'tempo' in perfil:
        partes.append(f"tem {perfil['tempo']} minutos por sessão")
    if not partes:
        return ""
    return f"Perfil do aluno: {', '.join(partes)}. Adapte volume e divisão a esse perfil. "


def _formato_resposta(perfil: Dict[str, Any]) -> str:
    """Fixed output format so clients can split the plan into days ('Treino A: ...' lines)."""
    dias = perfil.get('vezes_por_semana')
    divisao = f"Divida o plano em exatamente {dias} treinos. " if dias else ""
    return (
        f"{divisao}Responda sem introdução nem conclusão. Comece cada treino com uma linha "
        f"exatamente no formato 'Treino A: <grupos musculares>' (depois Treino B, Treino C...) "
        f"e liste abaixo um exercício por linha no formato '- <exercício> — <séries>x<repetições>'."
    )


# Main model first; the lighter model is a fallback when the main one is overloaded
# ("This model is currently experiencing high demand"), which happens during usage spikes.
# GEMINI_MODELOS (comma-separated) overrides the list without a code change; Google retires
# models (gemini-2.5-flash-lite returned 404 for new keys in Oct 2026).
MODELOS_PADRAO = ("gemini-2.5-flash", "gemini-3.5-flash-lite")
TENTATIVAS_POR_MODELO = 2
ESPERA_ENTRE_TENTATIVAS = 2  # seconds
ERROS_TEMPORARIOS = (429, 500, 503)


def modelos_configurados() -> tuple:
    bruto = current_app.config.get('GEMINI_MODELOS') or ''
    modelos = tuple(m.strip() for m in bruto.split(',') if m.strip())
    return modelos or MODELOS_PADRAO


def _gerar_com_reserva(client, prompt: str):
    """Tries each configured model in order; moves on only for transient errors (overload / rate limit)."""
    ultimo_erro: Optional[Exception] = None
    for modelo in modelos_configurados():
        for tentativa in range(TENTATIVAS_POR_MODELO):
            try:
                return client.models.generate_content(model=modelo, contents=prompt)
            except Exception as exc:
                if getattr(exc, 'code', None) not in ERROS_TEMPORARIOS:
                    # Bad key or bad request: another model would fail the same way
                    current_app.logger.error(f"Erro na integração com Google Gemini API ({modelo}): {exc}")
                    raise RuntimeError(f"Falha na comunicação com o serviço de IA: {exc}") from exc
                ultimo_erro = exc
                current_app.logger.warning(f"Gemini {modelo} indisponível (tentativa {tentativa + 1}): {exc}")
                if tentativa + 1 < TENTATIVAS_POR_MODELO:
                    time.sleep(ESPERA_ENTRE_TENTATIVAS)
    current_app.logger.error(f"Todos os modelos do Gemini indisponíveis: {ultimo_erro}")
    raise RuntimeError(f"Falha na comunicação com o serviço de IA: {ultimo_erro}") from ultimo_erro


def generate_treino(objetivo: str, nivel: str, perfil: Optional[Dict[str, Any]] = None) -> str:
    """Generates a personalized workout plan using Gemini 2.5 Flash AI.

    Args:
        objetivo (str): Target fitness goal (e.g., 'Perda de gordura', 'Hipertrofia de pernas').
        nivel (str): User experience level ('iniciante', 'intermediario', 'avancado').
        perfil (dict, optional): altura, peso, idade, vezes_por_semana and tempo, when known.

    Returns:
        str: Generated workout instructions formatted in text/markdown.

    Raises:
        ValueError: If Gemini API key is missing or AI provider returns an empty response.
        Exception: If an unexpected error occurs during AI service invocation.
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key or api_key.strip() in ("", "SUA_CHAVE_DE_API", "SUA_CHAVE_DE_API_AQUI"):
        raise ValueError(
            "Chave de API do Gemini não configurada. Defina a variável GEMINI_API_KEY no arquivo .env."
        )

    client = genai.Client(api_key=api_key)
    prompt_ia = (
        f"Você é um personal trainer altamente qualificado. "
        f"Crie um treino estruturado e objetivo focado em '{objetivo}' para um aluno de nível '{nivel}'. "
        f"{_descrever_perfil(perfil or {})}"
        f"Inclua nomes de exercícios, número de séries e repetições recomendadas. "
        f"{_formato_resposta(perfil or {})}"
    )

    response = _gerar_com_reserva(client, prompt_ia)

    if not response or not getattr(response, 'text', None):
        raise ValueError("O modelo do Gemini não retornou nenhum conteúdo válido.")

    return response.text.strip()
