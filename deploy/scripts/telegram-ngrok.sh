#!/usr/bin/env bash
# Start ngrok tunnel and register a Telegram bot webhook automatically.
# Usage:
#   ./deploy/scripts/telegram-ngrok.sh [port] [--role hr|candidate]
#     port — local Django port (default: 8000)
#     role — which bot to register (default: hr)

set -euo pipefail

PORT=8000
ROLE=hr
while [[ $# -gt 0 ]]; do
  case "$1" in
    --role)
      ROLE="$2"; shift 2 ;;
    --role=*)
      ROLE="${1#*=}"; shift ;;
    *)
      PORT="$1"; shift ;;
  esac
done

if [[ "$ROLE" != "hr" && "$ROLE" != "candidate" ]]; then
  echo "❌ --role must be 'hr' or 'candidate' (got: $ROLE)"
  exit 1
fi

BACKEND_ENV="$(cd "$(dirname "$0")/../../backend" && pwd)/.env"
if [[ ! -f "$BACKEND_ENV" ]]; then
  echo "❌ backend/.env not found at $BACKEND_ENV"
  exit 1
fi

read_env() { grep -E "^$1=" "$BACKEND_ENV" | cut -d= -f2- | tr -d '[:space:]'; }

# Pick the right token + secret for the chosen role.
if [[ "$ROLE" == "hr" ]]; then
  BOT_TOKEN="$(read_env TELEGRAM_HR_BOT_TOKEN || true)"
  if [[ -z "${BOT_TOKEN:-}" ]]; then
    BOT_TOKEN="$(read_env TELEGRAM_BOT_TOKEN || true)"  # legacy fallback
  fi
  WEBHOOK_SECRET="$(read_env TELEGRAM_HR_WEBHOOK_SECRET || true)"
  if [[ -z "${WEBHOOK_SECRET:-}" ]]; then
    WEBHOOK_SECRET="$(read_env TELEGRAM_WEBHOOK_SECRET || true)"
  fi
else
  BOT_TOKEN="$(read_env TELEGRAM_CANDIDATE_BOT_TOKEN || true)"
  WEBHOOK_SECRET="$(read_env TELEGRAM_CANDIDATE_WEBHOOK_SECRET || true)"
fi

if [[ -z "${BOT_TOKEN:-}" ]]; then
  echo "❌ Telegram $ROLE bot token is not set in backend/.env"
  exit 1
fi

# Kill any existing ngrok process
pkill -f "ngrok http" 2>/dev/null || true
sleep 1

echo "🚀 Starting ngrok on port $PORT..."
ngrok http "$PORT" --log=stdout > /dev/null &
NGROK_PID=$!

# Wait for ngrok to be ready
NGROK_URL=""
for _ in {1..15}; do
  NGROK_URL="$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    tunnels = json.load(sys.stdin)['tunnels']
    for t in tunnels:
        if t['proto'] == 'https':
            print(t['public_url'])
            break
except Exception:
    pass
" 2>/dev/null || true)"
  if [[ -n "$NGROK_URL" ]]; then
    break
  fi
  sleep 1
done

if [[ -z "${NGROK_URL:-}" ]]; then
  echo "❌ Failed to get ngrok URL after 15s. Is ngrok running?"
  kill "$NGROK_PID" 2>/dev/null || true
  exit 1
fi

WEBHOOK_URL="${NGROK_URL}/api/telegram/${ROLE}/webhook/"
echo "🌐 ngrok URL: $NGROK_URL"
echo "📡 Setting Telegram $ROLE webhook: $WEBHOOK_URL"

PAYLOAD="{\"url\": \"$WEBHOOK_URL\""
if [[ -n "${WEBHOOK_SECRET:-}" ]]; then
  PAYLOAD="$PAYLOAD, \"secret_token\": \"$WEBHOOK_SECRET\""
fi
PAYLOAD="$PAYLOAD}"

RESPONSE="$(curl -s -X POST \
  "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")"

OK="$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok',''))" 2>/dev/null || true)"

if [[ "$OK" == "True" ]]; then
  echo "✅ Webhook registered successfully!"
  echo ""
  echo "   ngrok dashboard: http://127.0.0.1:4040"
  echo "   Webhook URL:     $WEBHOOK_URL"
  echo "   ngrok PID:       $NGROK_PID"
  echo ""
  echo "⚠️  Make sure Django and Celery are running to process updates."
  echo "   Press Ctrl+C to stop ngrok and remove webhook."
else
  DESC="$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('description','Unknown error'))" 2>/dev/null || true)"
  echo "❌ Failed to set webhook: $DESC"
  kill "$NGROK_PID" 2>/dev/null || true
  exit 1
fi

# Cleanup on exit: remove webhook and stop ngrok
cleanup() {
  echo ""
  echo "🧹 Removing Telegram webhook..."
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook" > /dev/null 2>&1
  echo "🛑 Stopping ngrok (PID $NGROK_PID)..."
  kill "$NGROK_PID" 2>/dev/null || true
  echo "Done."
}
trap cleanup EXIT INT TERM

# Keep running — ngrok logs go to /dev/null, user sees the dashboard at :4040
wait "$NGROK_PID"
