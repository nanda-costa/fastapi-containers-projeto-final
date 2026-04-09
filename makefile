.PHONY: help menu \
	up up-build down down-v build restart restart-api \
	logs logs-api logs-db ps health \
	shell shell-db inspect-api inspect-db \
	build-no-cache images prune \
	lint lint-flake8 format check test test-cov clean

# ── Variáveis ─────────────────────────────────────────────────────────────────
COMPOSE  = docker compose
API      = projeto_api
DB       = projeto_postgres
SRC_DIR  = app
APP_FILE := $(if $(wildcard main.py),main.py,$(SRC_DIR)/main.py)
PYTHON   ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PIP      := $(PYTHON) -m pip
FLAKE8   := $(PYTHON) -m flake8
BLACK    := $(PYTHON) -m black
ISORT    := $(PYTHON) -m isort

# ── Ajuda ─────────────────────────────────────────────────────────────────────
help: ## Mostra esta mensagem de ajuda
	@printf "\n\033[1;36mCiclo da Stack\033[0m\n"
	@printf "  make up             - sobe todos os serviços em background\n"
	@printf "  make up-build       - sobe tudo com rebuild das imagens\n"
	@printf "  make down           - para e remove containers\n"
	@printf "  make down-v         - para containers e remove volumes\n"
	@printf "  make build          - apenas reconstrói as imagens\n"
	@printf "  make restart        - reinicia todos os serviços\n"
	@printf "  make restart-api    - reinicia apenas a API\n"

	@printf "\n\033[1;36mDiagnóstico\033[0m\n"
	@printf "  make ps             - lista os containers em execução\n"
	@printf "  make logs           - acompanha logs de todos os serviços\n"
	@printf "  make logs-api       - acompanha logs apenas da API\n"
	@printf "  make logs-db        - acompanha logs apenas do banco\n"
	@printf "  make health         - checa o endpoint /health da API\n"

	@printf "\n\033[1;36mDepuração\033[0m\n"
	@printf "  make shell          - abre shell no container da API\n"
	@printf "  make shell-db       - abre psql no container do banco\n"
	@printf "  make inspect-api    - inspeciona o container da API\n"
	@printf "  make inspect-db     - inspeciona o container do banco\n"

	@printf "\n\033[1;36mImagens e Build\033[0m\n"
	@printf "  make build-no-cache - reconstrói imagens sem cache\n"
	@printf "  make images         - lista imagens Docker locais\n"
	@printf "  make prune          - remove recursos Docker não usados\n"

	@printf "\n\033[1;36mQualidade de Código\033[0m\n"
	@printf "  make lint           - verifica o código com flake8\n"
	@printf "  make format         - formata o código com black e isort\n"
	@printf "  make check          - verifica formatação sem alterar arquivos\n"
	@printf "  make test           - executa os testes com pytest\n"
	@printf "  make test-cov       - executa testes com cobertura\n"
	@printf "  make clean          - remove arquivos de cache\n"

	@printf "\n\033[1;36mExtra\033[0m\n"
	@printf "  make menu           - abre o menu interativo de Docker\n\n"

# ── Menu Interativo ───────────────────────────────────────────────────────────
menu: ## Abre o menu interativo com comandos Docker
	chmod +x docker-menu.sh && ./docker-menu.sh

# ── Docker Compose / Ciclo da Stack ───────────────────────────────────────────
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

# ── Logs / Diagnóstico ────────────────────────────────────────────────────────
logs: ## Acompanha logs de todos os serviços
	$(COMPOSE) logs -f

logs-api: ## Acompanha logs apenas da API
	$(COMPOSE) logs -f api

logs-db: ## Acompanha logs apenas do banco
	$(COMPOSE) logs -f postgres

ps: ## Lista os containers em execução
	$(COMPOSE) ps

health: ## Checa o endpoint /health da API
	curl -s http://localhost:8000/health | python3 -m json.tool

# ── Shell / Depuração ─────────────────────────────────────────────────────────
shell: ## Abre shell no container da API
	$(COMPOSE) exec api sh

shell-db: ## Abre psql no container do banco
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

inspect-api: ## Mostra detalhes completos do container da API
	docker inspect $(API)

inspect-db: ## Mostra detalhes completos do container do banco
	docker inspect $(DB)

# ── Imagens e Build ───────────────────────────────────────────────────────────
build-no-cache: ## Reconstrói as imagens sem usar cache
	$(COMPOSE) build --no-cache

images: ## Lista imagens Docker locais
	docker images

prune: ## Remove recursos Docker não utilizados
	docker system prune

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