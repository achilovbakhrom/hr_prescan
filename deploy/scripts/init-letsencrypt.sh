#!/usr/bin/env bash
# =============================================================================
# init-letsencrypt.sh — Obtain Let's Encrypt TLS certificates via Certbot
#
# Usage:
#   DOMAIN=hrprescan.com EMAIL=admin@hrprescan.com ./scripts/init-letsencrypt.sh
#
# Environment variables:
#   DOMAIN        Primary domain (required)
#   EMAIL         ACME account email (required)
#   STAGING       Set to 1 to use Let's Encrypt staging (default: 0)
#   COMPOSE_FILE  Path to docker-compose files (default: base + prod)
# =============================================================================
set -euo pipefail

DOMAIN="${DOMAIN:?DOMAIN is required}"
EMAIL="${EMAIL:?EMAIL is required}"
STAGING="${STAGING:-0}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml -f docker-compose.prod.yml}"

CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
WEBROOT="/var/www/certbot"
DATA_PATH="/etc/letsencrypt"

echo "========================================="
echo " HR PreScan — Let's Encrypt Init Script"
echo " Domain : ${DOMAIN}"
echo " Email  : ${EMAIL}"
echo " Staging: ${STAGING}"
echo "========================================="

# --- 1. Create required directories ---
mkdir -p "${DATA_PATH}"
mkdir -p "${WEBROOT}"
mkdir -p /etc/nginx

# Generate dhparam for nginx if missing (needed by nginx.prod.conf.template)
if [ ! -f /etc/nginx/dhparam.pem ]; then
    echo "[INFO] Generating /etc/nginx/dhparam.pem (2048 bit, ~30s)..."
    openssl dhparam -out /etc/nginx/dhparam.pem 2048 2>/dev/null
fi

# --- 2. Check for existing certificate ---
if [ -d "${CERT_DIR}" ]; then
    echo "[INFO] Certificate already exists at ${CERT_DIR}"
    echo "[INFO] To renew, run: certbot renew"
    exit 0
fi

# --- 3. Download recommended TLS parameters (if not present) ---
if [ ! -f "${DATA_PATH}/ssl-dhparams.pem" ]; then
    echo "[INFO] Downloading recommended TLS DH parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
        -o "${DATA_PATH}/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem \
        -o "${DATA_PATH}/ssl-dhparams.pem"
fi

# --- 4. Generate a self-signed certificate as placeholder so nginx starts ---
echo "[INFO] Creating placeholder self-signed certificate..."
mkdir -p "${CERT_DIR}"
openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout "${CERT_DIR}/privkey.pem" \
    -out "${CERT_DIR}/fullchain.pem" \
    -subj "/CN=localhost" 2>/dev/null
cp "${CERT_DIR}/fullchain.pem" "${CERT_DIR}/chain.pem"

# --- 5. Start nginx (needs to serve ACME challenges) ---
echo "[INFO] Starting nginx..."
docker compose -f ${COMPOSE_FILE} up --force-recreate -d nginx

echo "[INFO] Waiting for nginx to be ready..."
sleep 5

# --- 6. Remove placeholder certificate ---
rm -rf "${CERT_DIR}"

# --- 7. Build certbot arguments ---
# Set INCLUDE_WWW=0 to skip the www subdomain (e.g. for dev.prescreen-app.com)
INCLUDE_WWW="${INCLUDE_WWW:-1}"
CERTBOT_ARGS=(
    certonly
    --webroot
    --webroot-path="${WEBROOT}"
    --email "${EMAIL}"
    --agree-tos
    --no-eff-email
    -d "${DOMAIN}"
)
if [ "${INCLUDE_WWW}" = "1" ]; then
    CERTBOT_ARGS+=(-d "www.${DOMAIN}")
fi

if [ "${STAGING}" = "1" ]; then
    echo "[WARN] Using Let's Encrypt STAGING environment (not trusted by browsers)"
    CERTBOT_ARGS+=(--staging)
fi

# --- 8. Obtain certificate ---
echo "[INFO] Requesting certificate from Let's Encrypt..."
docker run --rm \
    -v "${DATA_PATH}:/etc/letsencrypt" \
    -v "${WEBROOT}:/var/www/certbot" \
    certbot/certbot "${CERTBOT_ARGS[@]}"

echo "[INFO] Certificate obtained successfully."

# --- 9. Reload nginx with the real certificate ---
echo "[INFO] Reloading nginx..."
docker compose -f ${COMPOSE_FILE} exec nginx nginx -s reload

echo ""
echo "========================================="
echo " Certificate issued for ${DOMAIN}"
echo " Auto-renewal: add the following cron:"
echo "   0 0 * * * docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v ${WEBROOT}:/var/www/certbot certbot/certbot renew && docker compose exec nginx nginx -s reload"
echo "========================================="
