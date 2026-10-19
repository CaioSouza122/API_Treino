"""Main application entry point for API_Treino.

This module initializes the Flask application using the factory pattern.
Production: `gunicorn app:app` (settings in gunicorn.conf.py). Local: `python app.py`.
"""

from api_academia import create_app

# Create Flask application instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
