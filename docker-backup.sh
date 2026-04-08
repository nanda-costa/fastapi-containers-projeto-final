#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# docker-backup.sh — Backup e restauração do banco PostgreSQL containerizado
# Uso:
#   ./docker-backup.sh backup     → gera dump em backups/
#   ./docker-backup.sh restore    → restaura o dump mais recente
#   ./docker-backup.sh list       → lista backups disponíveis
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Configurações ─────────────────────────────────────────────────────────────
CONTAINER="projeto_postgres"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"

# Carrega variáveis do .env se existir
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

POSTGRES_USER="${POSTGRES_USER:-appuser}"
POSTGRES_DB="${POSTGRES_DB:-appdb}"

# ── Funções ───────────────────────────────────────────────────────────────────

backup() {
  echo "🔄 Iniciando backup do banco '${POSTGRES_DB}'..."
  mkdir -p "${BACKUP_DIR}"

  docker exec "${CONTAINER}" \
    pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" \
    | gzip > "${BACKUP_FILE}"

  echo "✅ Backup salvo em: ${BACKUP_FILE}"
  echo "📦 Tamanho: $(du -sh "${BACKUP_FILE}" | cut -f1)"
}

restore() {
  # Encontra o backup mais recente
  LATEST=$(ls -t "${BACKUP_DIR}"/*.sql.gz 2>/dev/null | head -n1 || true)

  if [ -z "${LATEST}" ]; then
    echo "❌ Nenhum backup encontrado em ${BACKUP_DIR}/"
    exit 1
  fi

  echo "⚠️  Restaurando: ${LATEST}"
  echo "   Banco alvo : ${POSTGRES_DB} @ ${CONTAINER}"
  read -p "   Confirma? [s/N] " confirm
  [[ "${confirm}" =~ ^[sS]$ ]] || { echo "Cancelado."; exit 0; }

  gunzip -c "${LATEST}" \
    | docker exec -i "${CONTAINER}" \
      psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

  echo "✅ Restore concluído com sucesso!"
}

list_backups() {
  echo "📂 Backups disponíveis em ${BACKUP_DIR}/:"
  if ls "${BACKUP_DIR}"/*.sql.gz 2>/dev/null; then
    echo ""
    echo "Total: $(ls "${BACKUP_DIR}"/*.sql.gz 2>/dev/null | wc -l) arquivo(s)"
  else
    echo "   Nenhum backup encontrado."
  fi
}

# ── Entry point ───────────────────────────────────────────────────────────────
case "${1:-}" in
  backup)  backup ;;
  restore) restore ;;
  list)    list_backups ;;
  *)
    echo "Uso: $0 {backup|restore|list}"
    exit 1
    ;;
esac
