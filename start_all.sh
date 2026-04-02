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

# 3b. Also update dashboard .env.local if it exists
DASHBOARD_ENV="$(dirname "$0")/../prodagentco-dashboard/.env.local"
if [ -f "$DASHBOARD_ENV" ]; then
    sed -i '' "s|^NEXT_PUBLIC_PIPELINE_URL=.*|NEXT_PUBLIC_PIPELINE_URL=$NGROK_URL|" "$DASHBOARD_ENV"
    echo "📝 Updated dashboard .env.local → NEXT_PUBLIC_PIPELINE_URL=$NGROK_URL"
fi

# 3c. Update Vercel env var and redeploy dashboard
VERCEL_TOKEN=$(grep "^VERCEL_TOKEN=" "$ENVFILE" | cut -d'=' -f2-)
VERCEL_PROJECT_ID=$(grep "^VERCEL_PROJECT_ID=" "$ENVFILE" | cut -d'=' -f2-)
if [ -n "$VERCEL_TOKEN" ] && [ -n "$VERCEL_PROJECT_ID" ]; then
    echo ""
    echo "🔄 Updating Vercel NEXT_PUBLIC_PIPELINE_URL..."

    # Check if the env var already exists
    EXISTING_ID=$(curl -s -H "Authorization: Bearer $VERCEL_TOKEN" \
        "https://api.vercel.com/v9/projects/$VERCEL_PROJECT_ID/env" \
        | python3 -c "
import sys, json
envs = json.load(sys.stdin).get('envs', [])
for e in envs:
    if e.get('key') == 'NEXT_PUBLIC_PIPELINE_URL':
        print(e['id'])
        break
" 2>/dev/null)

    if [ -n "$EXISTING_ID" ]; then
        # Update existing env var
        curl -s -X PATCH \
            -H "Authorization: Bearer $VERCEL_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"value\":\"$NGROK_URL\"}" \
            "https://api.vercel.com/v9/projects/$VERCEL_PROJECT_ID/env/$EXISTING_ID" > /dev/null
    else
        # Create new env var
        curl -s -X POST \
            -H "Authorization: Bearer $VERCEL_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"key\":\"NEXT_PUBLIC_PIPELINE_URL\",\"value\":\"$NGROK_URL\",\"type\":\"plain\",\"target\":[\"production\",\"preview\"]}" \
            "https://api.vercel.com/v9/projects/$VERCEL_PROJECT_ID/env" > /dev/null
    fi
    echo "✅ Vercel env var updated → NEXT_PUBLIC_PIPELINE_URL=$NGROK_URL"

    # Get repoId for deploy API
    REPO_ID=$(curl -s -H "Authorization: Bearer $VERCEL_TOKEN" \
        "https://api.vercel.com/v9/projects/$VERCEL_PROJECT_ID" \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('link',{}).get('repoId',''))" 2>/dev/null)

    # Trigger redeploy
    DEPLOY_RESULT=$(curl -s -X POST \
        -H "Authorization: Bearer $VERCEL_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"prodagentco-dashboard\",\"project\":\"$VERCEL_PROJECT_ID\",\"target\":\"production\",\"gitSource\":{\"type\":\"github\",\"repoId\":\"$REPO_ID\",\"ref\":\"main\"}}" \
        "https://api.vercel.com/v13/deployments")
    DEPLOY_URL=$(echo "$DEPLOY_RESULT" | python3 -c "
import sys, json, re
raw = sys.stdin.read()
clean = re.sub(r'[\x00-\x1f\x7f]', '', raw)
try:
    print(json.loads(clean).get('url',''))
except: pass
" 2>/dev/null)
    if [ -n "$DEPLOY_URL" ]; then
        echo "🚀 Vercel redeploy triggered → https://$DEPLOY_URL"
    else
        # Check if the response had alias (still a success)
        if echo "$DEPLOY_RESULT" | grep -q '"alias"'; then
            echo "🚀 Vercel redeploy triggered successfully"
        else
            echo "⚠️  Redeploy may have failed — check Vercel dashboard"
        fi
    fi
else
    echo ""
    echo "⚠️  VERCEL_TOKEN or VERCEL_PROJECT_ID not set — skipping Vercel update."
    echo "   Set them in .env to auto-update the dashboard on each start."
fi

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
