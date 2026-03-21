#!/usr/bin/env bash
# =============================================================================
# backup-db.sh — PostgreSQL backup with rotation
#
# Creates gzip-compressed pg_dump with timestamp.
# Retention: 7 daily, 4 weekly, 3 monthly backups.
#
# Usage:
#   ./scripts/backup-db.sh
#
# Environment variables (can be set in /etc/environment or .env):
#   POSTGRES_HOST      default: postgres
#   POSTGRES_PORT      default: 5432
#   POSTGRES_DB        required
#   POSTGRES_USER      required
#   PGPASSWORD         required (pg_dump reads this automatically)
#   BACKUP_DIR         default: /var/backups/hr_prescan
#   DOCKER_CONTAINER   if set, runs pg_dump inside the named container
# =============================================================================
set -euo pipefail

# --- Configuration ---
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:?POSTGRES_DB is required}"
POSTGRES_USER="${POSTGRES_USER:?POSTGRES_USER is required}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/hr_prescan}"
DOCKER_CONTAINER="${DOCKER_CONTAINER:-}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DAY_OF_WEEK=$(date +"%u")   # 1=Mon ... 7=Sun
DAY_OF_MONTH=$(date +"%d")

DAILY_DIR="${BACKUP_DIR}/daily"
WEEKLY_DIR="${BACKUP_DIR}/weekly"
MONTHLY_DIR="${BACKUP_DIR}/monthly"
LOG_FILE="${BACKUP_DIR}/backup.log"

# --- Helper ---
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"; }

# --- Create directories ---
mkdir -p "${DAILY_DIR}" "${WEEKLY_DIR}" "${MONTHLY_DIR}"

log "Starting backup of ${POSTGRES_DB}..."

BACKUP_FILE="${DAILY_DIR}/${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

# --- Run pg_dump ---
if [ -n "${DOCKER_CONTAINER}" ]; then
    log "Dumping via Docker container: ${DOCKER_CONTAINER}"
    docker exec -e PGPASSWORD="${PGPASSWORD}" "${DOCKER_CONTAINER}" \
        pg_dump -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" \
                -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
                --no-password --format=plain \
        | gzip > "${BACKUP_FILE}"
else
    log "Dumping directly via pg_dump"
    PGPASSWORD="${PGPASSWORD}" pg_dump \
        -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" \
        -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        --no-password --format=plain \
        | gzip > "${BACKUP_FILE}"
fi

BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
log "Daily backup created: ${BACKUP_FILE} (${BACKUP_SIZE})"

# --- Weekly backup (every Sunday) ---
if [ "${DAY_OF_WEEK}" = "7" ]; then
    WEEKLY_FILE="${WEEKLY_DIR}/${POSTGRES_DB}_week_${TIMESTAMP}.sql.gz"
    cp "${BACKUP_FILE}" "${WEEKLY_FILE}"
    log "Weekly backup created: ${WEEKLY_FILE}"
fi

# --- Monthly backup (1st of each month) ---
if [ "${DAY_OF_MONTH}" = "01" ]; then
    MONTHLY_FILE="${MONTHLY_DIR}/${POSTGRES_DB}_month_${TIMESTAMP}.sql.gz"
    cp "${BACKUP_FILE}" "${MONTHLY_FILE}"
    log "Monthly backup created: ${MONTHLY_FILE}"
fi

# --- Rotation ---
log "Rotating daily backups (keeping 7)..."
ls -1t "${DAILY_DIR}"/*.sql.gz 2>/dev/null | tail -n +8 | xargs -r rm -v | while read -r line; do
    log "Deleted old daily: ${line}"
done

log "Rotating weekly backups (keeping 4)..."
ls -1t "${WEEKLY_DIR}"/*.sql.gz 2>/dev/null | tail -n +5 | xargs -r rm -v | while read -r line; do
    log "Deleted old weekly: ${line}"
done

log "Rotating monthly backups (keeping 3)..."
ls -1t "${MONTHLY_DIR}"/*.sql.gz 2>/dev/null | tail -n +4 | xargs -r rm -v | while read -r line; do
    log "Deleted old monthly: ${line}"
done

log "Backup completed successfully."

# --- Summary ---
DAILY_COUNT=$(ls -1 "${DAILY_DIR}"/*.sql.gz 2>/dev/null | wc -l)
WEEKLY_COUNT=$(ls -1 "${WEEKLY_DIR}"/*.sql.gz 2>/dev/null | wc -l)
MONTHLY_COUNT=$(ls -1 "${MONTHLY_DIR}"/*.sql.gz 2>/dev/null | wc -l)
log "Retention: daily=${DAILY_COUNT}/7  weekly=${WEEKLY_COUNT}/4  monthly=${MONTHLY_COUNT}/3"
