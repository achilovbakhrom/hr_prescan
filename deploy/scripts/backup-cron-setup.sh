#!/usr/bin/env bash
# =============================================================================
# backup-cron-setup.sh — Install PostgreSQL backup cron job
#
# Installs a daily cron at 02:00 AM for the current user (or root).
# Run as: sudo ./scripts/backup-cron-setup.sh
#
# Environment variables:
#   BACKUP_SCRIPT   Path to backup-db.sh (default: auto-detect from script dir)
#   ENV_FILE        Path to env file with DB credentials (default: /etc/hr_prescan/backup.env)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${BACKUP_SCRIPT:-${SCRIPT_DIR}/backup-db.sh}"
ENV_FILE="${ENV_FILE:-/etc/hr_prescan/backup.env}"
CRON_LOG="/var/log/hr_prescan_backup.log"
CRON_USER="${SUDO_USER:-root}"

echo "============================================="
echo " HR PreScan — Backup Cron Installer"
echo " Script  : ${BACKUP_SCRIPT}"
echo " Env file: ${ENV_FILE}"
echo " Cron user: ${CRON_USER}"
echo "============================================="

# --- Validate backup script ---
if [ ! -f "${BACKUP_SCRIPT}" ]; then
    echo "[ERROR] Backup script not found: ${BACKUP_SCRIPT}"
    exit 1
fi
chmod +x "${BACKUP_SCRIPT}"

# --- Create env file directory ---
mkdir -p "$(dirname "${ENV_FILE}")"

# --- Create env file template if missing ---
if [ ! -f "${ENV_FILE}" ]; then
    echo "[INFO] Creating env file template at ${ENV_FILE}"
    cat > "${ENV_FILE}" <<'ENVEOF'
# HR PreScan backup environment variables
# Fill in real values before running backups.
POSTGRES_DB=hr_prescan
POSTGRES_USER=postgres
PGPASSWORD=changeme
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
BACKUP_DIR=/var/backups/hr_prescan
# Uncomment if running pg_dump inside a Docker container:
# DOCKER_CONTAINER=hr_prescan_postgres_1
ENVEOF
    chmod 600 "${ENV_FILE}"
    echo "[WARN] Please fill in credentials in ${ENV_FILE} before backups run."
fi

# --- Create log file ---
touch "${CRON_LOG}"
chmod 640 "${CRON_LOG}"

# --- Install cron job ---
CRON_JOB="0 2 * * * . ${ENV_FILE} && ${BACKUP_SCRIPT} >> ${CRON_LOG} 2>&1"

# Check if cron job already installed
EXISTING=$(crontab -u "${CRON_USER}" -l 2>/dev/null || true)
if echo "${EXISTING}" | grep -qF "${BACKUP_SCRIPT}"; then
    echo "[INFO] Cron job already installed for user ${CRON_USER}. Skipping."
else
    echo "[INFO] Installing cron job for user ${CRON_USER}..."
    (echo "${EXISTING}"; echo "${CRON_JOB}") | crontab -u "${CRON_USER}" -
    echo "[OK] Cron job installed."
fi

# --- Also install weekly certbot renewal cron ---
CERTBOT_JOB="0 0 * * 0 docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v /var/www/certbot:/var/www/certbot certbot/certbot renew --quiet && docker exec nginx nginx -s reload >> /var/log/certbot_renewal.log 2>&1"

EXISTING=$(crontab -u "${CRON_USER}" -l 2>/dev/null || true)
if echo "${EXISTING}" | grep -qF "certbot renew"; then
    echo "[INFO] Certbot renewal cron already installed. Skipping."
else
    echo "[INFO] Installing certbot renewal cron..."
    (echo "${EXISTING}"; echo "${CERTBOT_JOB}") | crontab -u "${CRON_USER}" -
    echo "[OK] Certbot renewal cron installed."
fi

echo ""
echo "============================================="
echo " Installed cron jobs:"
crontab -u "${CRON_USER}" -l | grep -v "^#" | grep -v "^$" || true
echo "============================================="
echo ""
echo "Next steps:"
echo "  1. Fill in ${ENV_FILE} with real DB credentials"
echo "  2. Test manually: ${BACKUP_SCRIPT}"
echo "  3. Check logs: tail -f ${CRON_LOG}"
