from flask import current_app
from google import genai

def generate_treino(objetivo: str, nivel: str) -> str:
    """Calls Gemini 2.5 Flash to generate a 3-exercise workout plan.
    
    Args:
        objetivo (str): The primary training goal.
        nivel (str): The level (iniciante, intermediario, avancado).
        
    Returns:
        str: Generated workout text.
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key or api_key == "SUA_CHAVE_DE_API" or api_key.strip() == "":
        raise ValueError("Chave de API do Gemini não configurada. Defina GEMINI_API_KEY no .env.")

    # Initialize the official Google GenAI Client
    client = genai.Client(api_key=api_key)
    
    # AI Prompt instruction
    prompt_ia = f"Crie um treino curto de 3 exercícios focado em '{objetivo}' para nível '{nivel}'."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_ia,
    )
    
    if not response or not response.text:
        raise ValueError("O modelo do Gemini não retornou nenhum conteúdo.")
        
    return response.text
