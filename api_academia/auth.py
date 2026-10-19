"""Authentication decorators and security middleware for api_academia.
"""

import hmac
from functools import wraps
from typing import Callable, Any
from flask import request, jsonify, current_app


def require_api_key(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator requiring a valid X-API-KEY header in incoming requests.

    If API_AUTH_KEY is empty, authentication is bypassed. create_app() only allows
    that in debug/testing mode, so production always requires the key.
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        expected_key = current_app.config.get('API_AUTH_KEY')

        # If expected key is not set or empty, disable auth check (development mode)
        if not expected_key or not expected_key.strip():
            return f(*args, **kwargs)

        provided_key = request.headers.get('X-API-KEY') or ''
        # Constant-time comparison avoids leaking the key through response timing
        if not hmac.compare_digest(provided_key.encode(), expected_key.encode()):
            return jsonify({
                'erro': 'Acesso não autorizado',
                'mensagem': 'Por favor, forneça um X-API-KEY válido no cabeçalho da requisição.'
            }), 401

        return f(*args, **kwargs)
    return decorated
