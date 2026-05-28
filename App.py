import sys
from pathlib import Path

# Add the package directory to the path to resolve imports
sys.path.insert(0, str(Path(__file__).parent))

from api_academia import create_app

# Instantiate the configured Flask app using the factory pattern
app = create_app()

@app.route('/')
def home():
    """Simple greeting page for browsers to confirm the API is online."""
    return (
        "<h1>API de Treinos com IA Online!</h1>"
        "<p>O backend está funcionando de forma robusta e persistente.</p>"
        "<p>Para interagir com os endpoints RESTful, use o Postman ou integre com o seu Frontend:</p>"
        "<ul>"
        "  <li><strong>Health Check:</strong> GET <code>/api/v1/health</code></li>"
        "  <li><strong>Criar Treino (POST):</strong> POST <code>/api/v1/treino</code></li>"
        "  <li><strong>Listar Treinos (GET):</strong> GET <code>/api/v1/treinos</code></li>"
        "  <li><strong>Deletar Treino (DELETE):</strong> DELETE <code>/api/v1/treino/&lt;id&gt;</code></li>"
        "</ul>"
    )

if __name__ == '__main__':
    # Run the app. Debug settings are loaded from .env automatically.
    app.run(host='0.0.0.0', port=5000)