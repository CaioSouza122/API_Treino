from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask-Limiter using the client's remote IP address
# Defaults to 100 requests per day and 30 per hour across all routes.
# Stricter custom limits can be applied to specific routes (e.g., Gemini endpoint)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day", "30 per hour"],
    storage_uri="memory://"  # In-memory rate limiting, perfect for SQLite/PostgreSQL setups
)
