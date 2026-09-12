"""Main application entry point for API_Treino.

This module initializes the Flask application using the factory pattern
and configures the root landing route for health & documentation guidance.
"""

import sys
from pathlib import Path

# Add package root directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from api_academia import create_app

# Create Flask application instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
