"""Test runner script for executing the full Pytest suite.

Allows developers to run all unit and integration tests with a single command:
    python run_tests.py
"""

import sys
import pytest

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Executando Suíte de Testes Automatizados da API_Treino")
    print("=" * 60)
    exit_code = pytest.main(["-v", "tests/"])
    sys.exit(exit_code)
