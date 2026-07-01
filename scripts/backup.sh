#!/bin/bash
# Daily PostgreSQL backup with 7-day local retention.
# Schedule: 0 2 * * * /scripts/backup.sh
#
# Required env vars:
#   DATABASE_URL  - PostgreSQL connection string
#   BACKUP_DIR    - Directory to store backups (default: /backups)

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
DB_URL="${DATABASE_URL:-}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.sql.gz"
LOG_FILE="${BACKUP_DIR}/backup.log"
RETENTION_DAYS=7

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${LOG_FILE}"
}

if [[ -z "${DB_URL}" ]]; then
    log "ERROR: DATABASE_URL is not set — aborting"
    exit 1
fi

mkdir -p "${BACKUP_DIR}"

log "Starting backup to ${BACKUP_FILE}"
if pg_dump "${DB_URL}" | gzip > "${BACKUP_FILE}"; then
    BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
    log "Backup completed successfully (${BACKUP_SIZE})"
else
    log "ERROR: pg_dump failed"
    rm -f "${BACKUP_FILE}"
    exit 1
fi

# Prune backups older than RETENTION_DAYS
DELETED=$(find "${BACKUP_DIR}" -name "backup_*.sql.gz" -mtime "+${RETENTION_DAYS}" -print -delete | wc -l)
log "Pruned ${DELETED} backup(s) older than ${RETENTION_DAYS} days"

log "Done"
