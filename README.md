# 🐳 Projeto Final — Fundamentos de Containers

> **Aula 08 · 09/04/2026 · Prof. Fabio Santos da Silva**  
> API FastAPI + PostgreSQL containerizada com Docker Compose

---

## 📋 Visão Geral

Este projeto implementa uma **API REST** completa em **Python/FastAPI**, containerizada com **Docker** e orquestrada via **Docker Compose**, atendendo a todos os critérios da avaliação final do curso.

### Stack

| Camada | Tecnologia |
|--------|-----------|
| API | Python 3.12 + FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 |
| Banco | PostgreSQL 16 (Alpine) |
| Container | Docker + Docker Compose |

---

## 🗂️ Estrutura do Projeto

```
fastapi-project/
├── app/
│   ├── __init__.py
│   ├── main.py          # Rotas FastAPI
│   ├── database.py      # Conexão SQLAlchemy
│   ├── models.py        # Modelos ORM
│   └── schemas.py       # Schemas Pydantic
├── backups/             # Gerado pelo docker-backup.sh
├── .dockerignore
├── .env.example         # ← copie para .env
├── .gitignore
├── docker-backup.sh     # Script de backup/restore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Como Rodar

### 1. Pré-requisitos

- Docker ≥ 24 e Docker Compose ≥ 2.20 instalados
- `git clone` ou download do projeto

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env e troque a senha padrão!
nano .env
```

### 3. Subir a stack

```bash
docker compose up -d --build
```

> A API aguarda o banco estar saudável antes de iniciar (healthcheck + `depends_on`).

### 4. Verificar

```bash
# Status dos serviços
docker compose ps

# Health check da API
curl http://localhost:8000/health
# → {"status":"ok","db":"connected"}

# Documentação interativa
open http://localhost:8000/docs
```

---

## 📡 Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Health check (API + DB) |
| `POST` | `/items` | Criar item |
| `GET` | `/items` | Listar itens |
| `GET` | `/items/{id}` | Buscar item por ID |
| `PUT` | `/items/{id}` | Atualizar item |
| `DELETE` | `/items/{id}` | Remover item |

### Exemplo de uso

```bash
# Criar item
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Notebook", "description": "Dell XPS 16GB", "active": true}'

# Listar itens
curl http://localhost:8000/items
```

---

## 💾 Backup e Restore

```bash
# Tornar o script executável (uma vez)
chmod +x docker-backup.sh

# Fazer backup
./docker-backup.sh backup

# Listar backups disponíveis
./docker-backup.sh list

# Restaurar o backup mais recente
./docker-backup.sh restore
```

Os backups ficam comprimidos em `./backups/backup_YYYYMMDD_HHMMSS.sql.gz`.

---

## 🔧 Comandos Úteis

```bash
# Subir com rebuild
docker compose up -d --build

# Ver logs da API em tempo real
docker compose logs -f api

# Ver logs do banco
docker compose logs postgres

# Abrir shell no container da API
docker compose exec api sh

# Acessar o banco via psql
docker compose exec postgres psql -U appuser -d appdb

# Parar e remover containers (dados persistem no volume!)
docker compose down

# Parar e remover TUDO incluindo volumes (⚠️ apaga dados!)
docker compose down -v

# Reiniciar apenas a API
docker compose restart api
```

---

## 🔐 Boas Práticas Implementadas

- ✅ **Usuário não-root** (`appuser`) no container da API
- ✅ **Senhas apenas no `.env`** — nunca no código ou Compose
- ✅ **`.dockerignore`** excluindo `.env` e `__pycache__`
- ✅ **Healthcheck** no PostgreSQL + `depends_on: condition: service_healthy`
- ✅ **Volume nomeado** para persistência dos dados do banco
- ✅ **Rede isolada** entre os serviços (`app_network`)
- ✅ **Tag de versão específica** nas imagens (`python:3.12-slim`, `postgres:16-alpine`)

---

## 📊 Critérios de Avaliação

| Critério | Pts | Status |
|----------|-----|--------|
| Dockerfile correto (imagem oficial, tag, non-root, .dockerignore) | 20 | ✅ |
| docker-compose.yml funcional (serviços, rede, volume) | 25 | ✅ |
| Segurança e boas práticas (.env, healthcheck, depends_on) | 20 | ✅ |
| Stack funcionando ao vivo (up -d, /health, persistência) | 35 | ✅ |
| **Total** | **100** | 🏆 |

---

## 🚀 Próximos Passos

- **Kubernetes** — orquestração em escala
- **CI/CD** com GitHub Actions
- **Docker em Cloud** — AWS ECS / GCP Cloud Run
- **Monitoramento** com Prometheus + Grafana
