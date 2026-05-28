from functools import wraps
from flask import request, jsonify, current_app

def require_api_key(f):
    """Decorator to require an X-API-KEY header in requests.
    
    If API_AUTH_KEY is not defined in the environment or configuration,
    the decorator allows the request to pass through without validation (dev mode).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        expected_key = current_app.config.get('API_AUTH_KEY')
        
        # If expected key is not set or is empty, disable auth checks
        if not expected_key or expected_key.strip() == "":
            return f(*args, **kwargs)
            
        provided_key = request.headers.get('X-API-KEY')
        if not provided_key or provided_key != expected_key:
            return jsonify({
                'erro': 'Acesso não autorizado. Por favor, forneça um X-API-KEY válido no cabeçalho da requisição.'
            }), 401
            
        return f(*args, **kwargs)
    return decorated
