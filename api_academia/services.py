"""Service layer handling AI integrations and business logic.

This module isolates calls to the official Google GenAI SDK (Gemini 2.5 Flash),
ensuring clean separation of concerns from HTTP controllers and routes.
"""

from flask import current_app
from google import genai


def generate_treino(objetivo: str, nivel: str) -> str:
    """Generates a personalized workout plan using Gemini 2.5 Flash AI.

    Args:
        objetivo (str): Target fitness goal (e.g., 'Perda de gordura', 'Hipertrofia de pernas').
        nivel (str): User experience level ('iniciante', 'intermediario', 'avancado').

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
        f"Inclua nomes de exercícios, número de séries e repetições recomendadas."
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_ia,
        )
    except Exception as exc:
        current_app.logger.error(f"Erro na integração com Google Gemini API: {exc}")
        raise RuntimeError(f"Falha na comunicação com o serviço de IA: {str(exc)}") from exc

    if not response or not getattr(response, 'text', None):
        raise ValueError("O modelo do Gemini não retornou nenhum conteúdo válido.")

    return response.text.strip()
