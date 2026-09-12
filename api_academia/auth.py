"""Authentication decorators and security middleware for api_academia.
"""

from functools import wraps
from typing import Callable, Any
from flask import request, jsonify, current_app


def require_api_key(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator requiring a valid X-API-KEY header in incoming requests.

    If API_AUTH_KEY is not defined or is empty in the app config,
    authentication is bypassed to facilitate local development/testing.
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        expected_key = current_app.config.get('API_AUTH_KEY')

        # If expected key is not set or empty, disable auth check (development mode)
        if not expected_key or not expected_key.strip():
            return f(*args, **kwargs)

        provided_key = request.headers.get('X-API-KEY')
        if not provided_key or provided_key != expected_key:
            return jsonify({
                'erro': 'Acesso não autorizado',
                'mensagem': 'Por favor, forneça um X-API-KEY válido no cabeçalho da requisição.'
            }), 401

        return f(*args, **kwargs)
    return decorated
