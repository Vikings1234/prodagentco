#!/usr/bin/env python3
"""Start the Telegram webhook server for Gate 1 replies."""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from gates.telegram_webhook import app, register_webhook

WEBHOOK_PORT = 5001


if __name__ == "__main__":
    webhook_url = os.getenv("WEBHOOK_URL")

    if webhook_url:
        register_webhook(f"{webhook_url}/webhook")
    else:
        print("⚠️  WEBHOOK_URL not set in .env — skipping Telegram registration.")
        print("   Set WEBHOOK_URL to your public URL (e.g. ngrok) and restart,")
        print("   or register manually: POST https://api.telegram.org/bot<token>/setWebhook")

    print(f"\n🚀 Gate 1 webhook server starting on port {WEBHOOK_PORT}...")
    app.run(host="0.0.0.0", port=WEBHOOK_PORT)
