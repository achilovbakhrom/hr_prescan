#!/usr/bin/env bash
# Start ngrok tunnel and register Telegram webhook automatically.
# Usage: ./deploy/scripts/telegram-ngrok.sh [port]
#   port — local Django port (default: 8000)

set -euo pipefail

PORT="${1:-8000}"
BACKEND_ENV="$(cd "$(dirname "$0")/../../backend" && pwd)/.env"

# Load TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET from backend/.env
if [[ -f "$BACKEND_ENV" ]]; then
  TELEGRAM_BOT_TOKEN="$(grep -E '^TELEGRAM_BOT_TOKEN=' "$BACKEND_ENV" | cut -d= -f2- | tr -d '[:space:]')"
  TELEGRAM_WEBHOOK_SECRET="$(grep -E '^TELEGRAM_WEBHOOK_SECRET=' "$BACKEND_ENV" | cut -d= -f2- | tr -d '[:space:]')"
else
  echo "❌ backend/.env not found at $BACKEND_ENV"
  exit 1
fi

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "❌ TELEGRAM_BOT_TOKEN is not set in backend/.env"
  exit 1
fi

# Kill any existing ngrok process
pkill -f "ngrok http" 2>/dev/null || true
sleep 1

echo "🚀 Starting ngrok on port $PORT..."
ngrok http "$PORT" --log=stdout > /dev/null &
NGROK_PID=$!

# Wait for ngrok to be ready
for i in {1..15}; do
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

WEBHOOK_URL="${NGROK_URL}/api/telegram/webhook/"
echo "🌐 ngrok URL: $NGROK_URL"
echo "📡 Setting Telegram webhook: $WEBHOOK_URL"

# Build setWebhook payload
PAYLOAD="{\"url\": \"$WEBHOOK_URL\""
if [[ -n "${TELEGRAM_WEBHOOK_SECRET:-}" ]]; then
  PAYLOAD="$PAYLOAD, \"secret_token\": \"$TELEGRAM_WEBHOOK_SECRET\""
fi
PAYLOAD="$PAYLOAD}"

RESPONSE="$(curl -s -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
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
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook" > /dev/null 2>&1
  echo "🛑 Stopping ngrok (PID $NGROK_PID)..."
  kill "$NGROK_PID" 2>/dev/null || true
  echo "Done."
}
trap cleanup EXIT INT TERM

# Keep running — ngrok logs go to /dev/null, user sees the dashboard at :4040
wait "$NGROK_PID"
