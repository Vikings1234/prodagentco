"""HITL Gates — Telegram notifications for approval gates."""

import os
import re
import requests


def send_telegram(message: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram credentials not set in .env")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    return response.status_code == 200


def gate1_notify(verdict, avg_confidence, agent_scores, lead_opportunity):
    if "GO" in verdict and "NEEDS" not in verdict:
        emoji = "OK"
    elif "NEEDS_HUMAN_REVIEW" in verdict:
        emoji = "REVIEW"
    else:
        emoji = "NO"

    scores_text = ""
    for agent, score in agent_scores.items():
        if float(score) >= 0.70:
            bar = "GREEN"
        elif float(score) >= 0.40:
            bar = "YELLOW"
        else:
            bar = "RED"
        scores_text += f"  {bar} {agent}: {score}\n"

    message = (
        "ProdAgentCo Gate 1 Decision Required\n\n"
        f"VERDICT: {verdict} {emoji}\n"
        f"Average Confidence: {avg_confidence}\n\n"
        f"Lead Opportunity: {lead_opportunity}\n\n"
        f"Agent Scores:\n{scores_text}\n"
        "Your Options:\n"
        "Reply APPROVE to proceed to Planning\n"
        "Reply KILL to archive\n"
        "Reply DEFER to add to backlog\n"
        "Reply REVISE to return to debate\n"
    )
    success = send_telegram(message)
    if success:
        print("Gate 1 notification sent to Telegram")
    else:
        print("Failed to send Telegram notification")


def gate1_parse_verdict(verdict_text):
    result = {
        "verdict": "NEEDS_HUMAN_REVIEW",
        "avg_confidence": 0.0,
        "lead_opportunity": "Unknown",
        "agent_scores": {}
    }
    lines = verdict_text.lower()
    if "final decision: go" in lines and "needs_human_review" not in lines:
        result["verdict"] = "GO"
    elif "needs_human_review" in lines:
        result["verdict"] = "NEEDS_HUMAN_REVIEW"
    elif "no-go" in lines or "no go" in lines:
        result["verdict"] = "NO-GO"
    conf_match = re.search(r'average confidence[:\s]+([0-9.]+)', lines)
    if conf_match:
        result["avg_confidence"] = float(conf_match.group(1))
    return result
