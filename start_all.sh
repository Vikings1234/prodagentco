#!/usr/bin/env bash
# Start ngrok + Flask webhook server together for Gate 1 Telegram integration.
set -e

PORT=5001
ENVFILE="$(dirname "$0")/.env"

cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $NGROK_PID $FLASK_PID 2>/dev/null || true
    wait $NGROK_PID $FLASK_PID 2>/dev/null || true
    echo "Done."
}
trap cleanup EXIT INT TERM

# 1. Start ngrok in the background
echo "🌐 Starting ngrok on port $PORT..."
ngrok http $PORT --log=stdout --log-level=warn > /dev/null 2>&1 &
NGROK_PID=$!
sleep 2

# 2. Grab the public URL from ngrok's local API
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "
import sys, json
tunnels = json.load(sys.stdin).get('tunnels', [])
for t in tunnels:
    if t.get('proto') == 'https':
        print(t['public_url'])
        break
" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Could not get ngrok URL. Is ngrok authenticated?"
    echo "   Run: ngrok config add-authtoken <your-token>"
    exit 1
fi

echo ""
echo "✅ ngrok public URL: $NGROK_URL"
echo ""

# 3. Write WEBHOOK_URL into .env so Flask picks it up
if grep -q "^WEBHOOK_URL=" "$ENVFILE"; then
    sed -i '' "s|^WEBHOOK_URL=.*|WEBHOOK_URL=$NGROK_URL|" "$ENVFILE"
else
    echo "WEBHOOK_URL=$NGROK_URL" >> "$ENVFILE"
fi
echo "📝 Updated .env → WEBHOOK_URL=$NGROK_URL"

# 4. Start Flask webhook server
echo ""
source "$(dirname "$0")/venv/bin/activate"
python "$(dirname "$0")/start_webhook.py" &
FLASK_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ngrok:  $NGROK_URL → localhost:$PORT"
echo "  Flask:  http://localhost:$PORT"
echo "  Health: http://localhost:$PORT/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop both services."
echo ""

wait
