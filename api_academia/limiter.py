import hashlib

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def client_key() -> str:
    """Rate-limit bucket: the API key when sent (one bucket per client project), else the IP.

    Behind Render's proxy every request from the HIPERTROF.IA backend arrives from the
    same address, so counting by IP alone would make all app users share one tiny quota.
    """
    api_key = request.headers.get('X-API-KEY')
    if api_key:
        return "key:" + hashlib.sha256(api_key.encode()).hexdigest()[:16]
    return "ip:" + get_remote_address()


# shortcut: memory storage is per gunicorn worker, so the real limit is N_workers x the value.
# Fine for 2 workers; switch storage_uri to Redis if the API scales out to several instances.
limiter = Limiter(
    key_func=client_key,
    default_limits=["600 per hour"],
    storage_uri="memory://"
)
