.PHONY: help install run test lint format docker-build docker-run clean

PYTHON = .venv/Scripts/python.exe
PIP = .venv/Scripts/pip.exe
PYTEST = .venv/Scripts/pytest.exe
FLAKE8 = .venv/Scripts/flake8.exe

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instala todas as dependências no ambiente virtual"
	@echo "  make run          - Inicia o servidor Flask em modo de desenvolvimento"
	@echo "  make test         - Executa os testes automatizados com Pytest"
	@echo "  make lint         - Executa a análise estática de código com Flake8"
	@echo "  make docker-build - Constrói a imagem Docker da aplicação"
	@echo "  make docker-run   - Roda o container Docker na porta 5000"
	@echo "  make clean        - Remove arquivos de cache e banco local de testes"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) app.py

test:
	$(PYTEST) tests/

lint:
	$(FLAKE8) . --count --select=E9,F63,F7,F82 --show-source --statistics

docker-build:
	docker build -t api-academia:latest .

docker-run:
	docker run -p 5000:5000 --env-file .env api-academia:latest

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -f api_academia.db
