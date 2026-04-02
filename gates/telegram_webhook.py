"""Telegram Webhook — listens for Gate 1 reply commands (APPROVE/KILL/DEFER/REVISE)."""

import os
import json
import datetime
import requests
from flask import Flask, request, jsonify
from config.settings import OUTPUT_DIR, LOG_DIR


app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, ngrok-skip-browser-warning"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

VALID_COMMANDS = {"APPROVE", "KILL", "DEFER", "REVISE", "APPROVE2", "REVISE2", "APPROVE3", "REVISE3"}


def log_decision(command: str, chat_id: int, text: str):
    """Append the human decision to logs/gate1_decisions.json."""
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / "gate1_decisions.json"

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "command": command,
        "chat_id": chat_id,
        "raw_text": text,
    }

    entries = []
    if log_file.exists():
        entries = json.loads(log_file.read_text())
    entries.append(entry)
    log_file.write_text(json.dumps(entries, indent=2))
    print(f"📝 Logged Gate 1 decision: {command}")


def reply_telegram(chat_id: int, text: str):
    """Send a confirmation reply back to Telegram."""
    token = os.getenv("PRODAGENTCO_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})


def handle_approve():
    """Trigger the planning phase (Phase 2)."""
    try:
        from pipelines.planning import run_planning_phase
        print("🚀 APPROVE received — launching Planning phase...")
        run_planning_phase()
    except ImportError:
        print("⏳ APPROVE received — run_planning_phase() not yet implemented, logged for now.")


def handle_kill():
    """Archive the opportunity."""
    archive_file = OUTPUT_DIR / "archived.json"
    brief_file = OUTPUT_DIR / "discovery-brief.md"

    entries = []
    if archive_file.exists():
        entries = json.loads(archive_file.read_text())

    entries.append({
        "archived_at": datetime.datetime.now().isoformat(),
        "brief": brief_file.read_text() if brief_file.exists() else "No brief found",
        "reason": "KILLED at Gate 1",
    })
    archive_file.write_text(json.dumps(entries, indent=2))
    print("🗄️ KILL received — opportunity archived.")


def handle_defer():
    """Add opportunity to backlog."""
    backlog_file = OUTPUT_DIR / "backlog.json"
    brief_file = OUTPUT_DIR / "discovery-brief.md"

    entries = []
    if backlog_file.exists():
        entries = json.loads(backlog_file.read_text())

    entries.append({
        "deferred_at": datetime.datetime.now().isoformat(),
        "brief": brief_file.read_text() if brief_file.exists() else "No brief found",
        "reason": "DEFERRED at Gate 1",
    })
    backlog_file.write_text(json.dumps(entries, indent=2))
    print("📋 DEFER received — opportunity added to backlog.")


def handle_revise():
    """Re-run the debate phase."""
    from pipelines.debate import run_debate_phase
    print("🔄 REVISE received — re-running debate phase...")
    result = run_debate_phase()

    verdict_file = OUTPUT_DIR / "debate-verdict.md"
    with open(verdict_file, "w") as f:
        f.write(str(result))
    print(f"✅ Revised debate saved to {verdict_file}")


def handle_approve2():
    """Trigger the build phase (Phase 3)."""
    from pipelines.build import run_build_phase
    print("🚀 APPROVE2 received — launching Build phase...")
    run_build_phase()


def handle_revise2():
    """Re-run the planning phase."""
    from pipelines.planning import run_planning_phase
    print("🔄 REVISE2 received — re-running planning phase...")
    run_planning_phase()


def handle_approve3():
    """Trigger Vercel deployment after build approval."""
    import os
    vercel_token = os.getenv("VERCEL_TOKEN")
    vercel_project = os.getenv("VERCEL_PROJECT_ID")

    if not vercel_token or not vercel_project:
        print("⚠️ APPROVE3 received — VERCEL_TOKEN or VERCEL_PROJECT_ID not set, skipping deploy.")
        return

    print("🚀 APPROVE3 received — triggering Vercel deployment...")
    import requests as req

    # Get repoId
    proj_resp = req.get(
        f"https://api.vercel.com/v9/projects/{vercel_project}",
        headers={"Authorization": f"Bearer {vercel_token}"}
    )
    repo_id = proj_resp.json().get("link", {}).get("repoId", "")

    # Trigger deploy
    deploy_resp = req.post(
        "https://api.vercel.com/v13/deployments",
        headers={"Authorization": f"Bearer {vercel_token}", "Content-Type": "application/json"},
        json={
            "name": "prodagentco-dashboard",
            "project": vercel_project,
            "target": "production",
            "gitSource": {"type": "github", "repoId": str(repo_id), "ref": "main"}
        }
    )
    if deploy_resp.status_code == 200:
        print("✅ Vercel deployment triggered")
    else:
        print(f"⚠️ Vercel deploy response: {deploy_resp.status_code}")


def handle_revise3():
    """Re-run the build phase."""
    from pipelines.build import run_build_phase
    print("🔄 REVISE3 received — re-running build phase...")
    run_build_phase()


HANDLERS = {
    "APPROVE": handle_approve,
    "KILL": handle_kill,
    "DEFER": handle_defer,
    "REVISE": handle_revise,
    "APPROVE2": handle_approve2,
    "REVISE2": handle_revise2,
    "APPROVE3": handle_approve3,
    "REVISE3": handle_revise3,
}

CONFIRMATIONS = {
    "APPROVE": "✅ *APPROVED* — launching Planning phase.",
    "KILL": "🗄️ *KILLED* — opportunity archived.",
    "DEFER": "📋 *DEFERRED* — added to backlog for later review.",
    "REVISE": "🔄 *REVISE* — re-running debate phase. You'll get a new verdict shortly.",
    "APPROVE2": "✅ *APPROVED (Gate 2)* — proceeding to Build phase.",
    "REVISE2": "🔄 *REVISE (Gate 2)* — re-running planning phase.",
    "APPROVE3": "🚀 *APPROVED (Gate 3)* — deploying to Vercel.",
    "REVISE3": "🔄 *REVISE (Gate 3)* — re-running build phase.",
}


@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"ok": True}), 200

    message = data["message"]
    text = message.get("text", "").strip().upper()
    chat_id = message["chat"]["id"]

    # Only accept messages from our configured chat
    expected_chat = os.getenv("PRODAGENTCO_CHAT_ID")
    if expected_chat and str(chat_id) != expected_chat:
        return jsonify({"ok": True}), 200

    if text not in VALID_COMMANDS:
        reply_telegram(chat_id, f"Unknown command: _{text}_\nValid options: APPROVE, KILL, DEFER, REVISE")
        return jsonify({"ok": True}), 200

    log_decision(text, chat_id, message.get("text", ""))
    reply_telegram(chat_id, CONFIRMATIONS[text])
    HANDLERS[text]()

    return jsonify({"ok": True}), 200


@app.route("/run", methods=["POST", "OPTIONS"])
def trigger_run():
    """Trigger a full pipeline run from the dashboard."""
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json(silent=True) or {}
    domain = data.get("domain", "agentic-payments")
    custom_query = data.get("customQuery")
    print(f"\n📡 Received /run request — domain: {domain}, customQuery: {custom_query}")

    import threading

    def run_pipeline():
        from pipelines.phase1 import run_discovery_phase
        from pipelines.debate import run_debate_phase
        from gates.hitl_gates import gate1_notify, gate1_parse_verdict
        from config.settings import DEBATE_CONFIDENCE_THRESHOLD

        print(f"\n🚀 Dashboard-triggered run — domain: {domain}")
        result = run_discovery_phase(domain=domain, custom_query=custom_query)

        output_file = OUTPUT_DIR / "discovery-brief.md"
        output_file.write_text(str(result))

        debate_result = run_debate_phase()
        verdict_file = OUTPUT_DIR / "debate-verdict.md"
        verdict_file.write_text(str(debate_result))

        parsed = gate1_parse_verdict(str(debate_result))
        avg_conf = parsed["avg_confidence"]
        verdict = parsed["verdict"]

        if verdict != "GO" or avg_conf < DEBATE_CONFIDENCE_THRESHOLD:
            import re as _re
            brief_text = (OUTPUT_DIR / "discovery-brief.md").read_text() if (OUTPUT_DIR / "discovery-brief.md").exists() else ""
            title_m = _re.search(r'RANK 1[:\s]*(?:\*\*)?([^*\n]+)', brief_text) or _re.search(r'LEAD RECOMMENDATION[:\s]*(?:Opportunity #\d+\s*—?\s*)?(.+)', brief_text)
            lead_opp = title_m.group(1).replace('**', '').strip() if title_m else "See discovery-brief.md"

            gate1_notify(
                verdict=verdict,
                avg_confidence=avg_conf,
                lead_opportunity=lead_opp,
                agent_scores=parsed.get("agent_scores", {})
            )

    threading.Thread(target=run_pipeline, daemon=True).start()
    return jsonify({"ok": True, "domain": domain, "status": "started"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


def register_webhook(webhook_url: str):
    """Register this server's URL with the Telegram Bot API."""
    token = os.getenv("PRODAGENTCO_BOT_TOKEN")
    if not token:
        print("❌ PRODAGENTCO_BOT_TOKEN not set in .env")
        return False

    url = f"https://api.telegram.org/bot{token}/setWebhook"
    resp = requests.post(url, json={"url": webhook_url})
    result = resp.json()

    if result.get("ok"):
        print(f"✅ Webhook registered: {webhook_url}")
        return True
    else:
        print(f"❌ Webhook registration failed: {result.get('description')}")
        return False
