.PHONY: help up down build restart logs shell lint lint-flake8 format check test clean

# ── Variáveis ─────────────────────────────────────────────────────────────────
COMPOSE  = docker compose
API      = projeto_api
SRC_DIR  = app
APP_FILE := $(if $(wildcard main.py),main.py,$(SRC_DIR)/main.py)
PYTHON   ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PIP      := $(PYTHON) -m pip
FLAKE8   := $(PYTHON) -m flake8
BLACK    := $(PYTHON) -m black
ISORT    := $(PYTHON) -m isort

# ── Ajuda ─────────────────────────────────────────────────────────────────────
help: ## Mostra esta mensagem de ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Docker Compose ────────────────────────────────────────────────────────────
up: ## Sobe todos os serviços em background
	$(COMPOSE) up -d

up-build: ## Reconstrói as imagens e sobe os serviços
	$(COMPOSE) up -d --build

down: ## Para e remove os containers
	$(COMPOSE) down

down-v: ## Para containers e remove volumes (apaga dados do banco)
	$(COMPOSE) down -v

build: ## Apenas reconstrói as imagens
	$(COMPOSE) build

restart: ## Reinicia todos os serviços
	$(COMPOSE) restart

restart-api: ## Reinicia apenas a API
	$(COMPOSE) restart api

# ── Logs ──────────────────────────────────────────────────────────────────────
logs: ## Acompanha logs de todos os serviços
	$(COMPOSE) logs -f

logs-api: ## Acompanha logs apenas da API
	$(COMPOSE) logs -f api

logs-db: ## Acompanha logs apenas do banco
	$(COMPOSE) logs -f postgres

# ── Shell ─────────────────────────────────────────────────────────────────────
shell: ## Abre bash no container da API
	$(COMPOSE) exec api bash

shell-db: ## Abre psql no container do banco
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

# ── Qualidade de Código ───────────────────────────────────────────────────────
lint: ## Verifica o código com flake8
	$(FLAKE8) $(SRC_DIR) $(APP_FILE)

lint-flake8: lint ## Alias para compatibilidade com chamadas antigas

format: ## Formata o código com black e isort
	$(ISORT) $(SRC_DIR) $(APP_FILE)
	$(BLACK) $(SRC_DIR) $(APP_FILE)

check: ## Verifica formatação sem modificar arquivos (CI)
	$(ISORT) --check-only $(SRC_DIR) $(APP_FILE)
	$(BLACK) --check $(SRC_DIR) $(APP_FILE)
	$(FLAKE8) $(SRC_DIR) $(APP_FILE)

# ── Testes ────────────────────────────────────────────────────────────────────
test: ## Executa os testes com pytest
	$(PYTHON) -m pytest -v

test-cov: ## Executa testes com relatório de cobertura
	$(PYTHON) -m pytest --cov=$(SRC_DIR) --cov-report=term-missing -v

# ── Utilitários ───────────────────────────────────────────────────────────────
ps: ## Lista os containers em execução
	$(COMPOSE) ps

health: ## Checa o endpoint /health da API
	curl -s http://localhost:8001/health | python3 -m json.tool

clean: ## Remove arquivos de cache Python
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete
	find . -name "test_api.db" -delete
	find . -name "test_bootstrap.db" -delete
