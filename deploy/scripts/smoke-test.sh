#!/usr/bin/env bash
# =============================================================================
# smoke-test.sh — Post-deployment smoke tests for HR PreScan
#
# Usage:
#   ./scripts/smoke-test.sh [BASE_URL]
#
# Arguments:
#   BASE_URL   e.g. https://hrprescan.com  (default: http://localhost)
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more checks failed
# =============================================================================
set -euo pipefail

BASE_URL="${1:-http://localhost}"
FAILURES=0

# Strip trailing slash
BASE_URL="${BASE_URL%/}"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; FAILURES=$((FAILURES + 1)); }
info() { echo -e "${YELLOW}[INFO]${NC} $*"; }

# ---------------------------------------------------------------------------
# Helper: HTTP check
#   check <description> <url> <expected_status> [expected_body_pattern]
# ---------------------------------------------------------------------------
check() {
    local desc="$1"
    local url="$2"
    local expected_status="$3"
    local body_pattern="${4:-}"

    local response
    local http_status

    response=$(curl -sk --max-time 15 -w "\n%{http_code}" "${url}" 2>&1) || {
        fail "${desc}: curl failed (connection refused or timeout)"
        return
    }

    http_status=$(echo "${response}" | tail -1)
    local body
    body=$(echo "${response}" | sed '$d')

    if [ "${http_status}" != "${expected_status}" ]; then
        fail "${desc}: expected HTTP ${expected_status}, got ${http_status} (${url})"
        return
    fi

    if [ -n "${body_pattern}" ]; then
        if ! echo "${body}" | grep -q "${body_pattern}"; then
            fail "${desc}: response body did not match '${body_pattern}'"
            return
        fi
    fi

    pass "${desc} (HTTP ${http_status})"
}

# ---------------------------------------------------------------------------
# 1. Health check endpoint
# ---------------------------------------------------------------------------
info "=== Check 1: Django health endpoint ==="
check "Health endpoint" "${BASE_URL}/api/health/" "200" "ok"

# ---------------------------------------------------------------------------
# 2. Nginx is serving (200 or redirect)
# ---------------------------------------------------------------------------
info "=== Check 2: Nginx / SPA root ==="
ROOT_STATUS=$(curl -sk --max-time 15 -o /dev/null -w "%{http_code}" "${BASE_URL}/" 2>/dev/null || echo "000")
if [[ "${ROOT_STATUS}" =~ ^(200|301|302)$ ]]; then
    pass "Nginx root (HTTP ${ROOT_STATUS})"
else
    fail "Nginx root returned HTTP ${ROOT_STATUS}"
fi

# ---------------------------------------------------------------------------
# 3. HTTPS redirect (only if BASE_URL starts with https)
# ---------------------------------------------------------------------------
if [[ "${BASE_URL}" == https://* ]]; then
    info "=== Check 3: HTTP → HTTPS redirect ==="
    HTTP_URL="${BASE_URL/https:\/\//http://}"
    REDIRECT_STATUS=$(curl -sk --max-time 10 -o /dev/null -w "%{http_code}" "${HTTP_URL}/" 2>/dev/null || echo "000")
    if [[ "${REDIRECT_STATUS}" =~ ^(301|302|308)$ ]]; then
        pass "HTTP→HTTPS redirect (HTTP ${REDIRECT_STATUS})"
    else
        fail "Expected HTTP redirect, got ${REDIRECT_STATUS}"
    fi
else
    info "=== Check 3: Skipped (not HTTPS) ==="
fi

# ---------------------------------------------------------------------------
# 4. API returns 401 for unauthenticated request
# ---------------------------------------------------------------------------
info "=== Check 4: API requires authentication ==="
check "API auth enforcement" "${BASE_URL}/api/vacancies/" "401"

# ---------------------------------------------------------------------------
# 5. Auth endpoint returns 400 for empty POST (not 500)
# ---------------------------------------------------------------------------
info "=== Check 5: Auth endpoint is responsive ==="
AUTH_STATUS=$(curl -sk --max-time 15 -o /dev/null -w "%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{}' \
    "${BASE_URL}/api/auth/login/" 2>/dev/null || echo "000")
if [[ "${AUTH_STATUS}" =~ ^(400|401|422)$ ]]; then
    pass "Auth endpoint responsive (HTTP ${AUTH_STATUS})"
else
    fail "Auth endpoint returned unexpected HTTP ${AUTH_STATUS}"
fi

# ---------------------------------------------------------------------------
# 6. Django admin is reachable (200 normally, 403 when IP-restricted in prod nginx)
# ---------------------------------------------------------------------------
info "=== Check 6: Django admin panel ==="
ADMIN_STATUS=$(curl -sk --max-time 15 -o /dev/null -w "%{http_code}" "${BASE_URL}/admin/" 2>/dev/null || echo "000")
if [[ "${ADMIN_STATUS}" =~ ^(200|302|403)$ ]]; then
    pass "Admin panel reachable (HTTP ${ADMIN_STATUS})"
else
    fail "Admin panel returned HTTP ${ADMIN_STATUS}"
fi

# ---------------------------------------------------------------------------
# 7. Prometheus metrics endpoint (optional — may not be wired up)
# ---------------------------------------------------------------------------
info "=== Check 7: Prometheus metrics (optional) ==="
METRICS_STATUS=$(curl -sk --max-time 10 -o /dev/null -w "%{http_code}" "${BASE_URL}/metrics" 2>/dev/null || echo "000")
if [[ "${METRICS_STATUS}" =~ ^(200|404)$ ]]; then
    pass "Metrics endpoint responded (HTTP ${METRICS_STATUS})"
else
    info "Metrics endpoint not available (HTTP ${METRICS_STATUS}) — skipping"
fi

# ---------------------------------------------------------------------------
# 8. Static files served
# ---------------------------------------------------------------------------
info "=== Check 8: Static/media reachability ==="
STATIC_STATUS=$(curl -sk --max-time 10 -o /dev/null -w "%{http_code}" \
    "${BASE_URL}/static/" 2>/dev/null || echo "000")
# 404 is acceptable for directory listing; 200 or 404 means nginx is routing correctly
if [[ "${STATIC_STATUS}" =~ ^(200|301|302|403|404)$ ]]; then
    pass "Static file routing (HTTP ${STATIC_STATUS})"
else
    fail "Static file routing returned ${STATIC_STATUS}"
fi

# ---------------------------------------------------------------------------
# 9. Security headers present
# ---------------------------------------------------------------------------
if [[ "${BASE_URL}" == https://* ]]; then
    info "=== Check 9: Security headers ==="
    HEADERS=$(curl -skI --max-time 15 "${BASE_URL}/" 2>/dev/null)

    if echo "${HEADERS}" | grep -qi "strict-transport-security"; then
        pass "HSTS header present"
    else
        fail "HSTS header missing"
    fi

    if echo "${HEADERS}" | grep -qi "x-content-type-options"; then
        pass "X-Content-Type-Options header present"
    else
        fail "X-Content-Type-Options header missing"
    fi

    if echo "${HEADERS}" | grep -qi "x-frame-options"; then
        pass "X-Frame-Options header present"
    else
        fail "X-Frame-Options header missing"
    fi
else
    info "=== Check 9: Skipped (not HTTPS) ==="
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "========================================="
if [ "${FAILURES}" -eq 0 ]; then
    echo -e "${GREEN}All smoke tests passed.${NC}"
    exit 0
else
    echo -e "${RED}${FAILURES} smoke test(s) FAILED.${NC}"
    exit 1
fi
