"""HITL Gates — Telegram notifications for approval gates."""

import os
import re
import requests


def send_telegram(message: str) -> bool:
    token = os.getenv("PRODAGENTCO_BOT_TOKEN")
    chat_id = os.getenv("PRODAGENTCO_CHAT_ID")
    if not token or not chat_id:
        print("Telegram credentials not set in .env")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    return response.status_code == 200


def extract_lead_opportunity(brief_path=None):
    """Extract lead opportunity title from discovery-brief.md."""
    from pathlib import Path
    from config.settings import OUTPUT_DIR

    p = Path(brief_path) if brief_path else OUTPUT_DIR / "discovery-brief.md"
    if not p.exists():
        return "See discovery-brief.md"

    text = p.read_text()
    lines = text.split('\n')

    # Find LEAD RECOMMENDATION line, then grab the next heading as the title
    for i, line in enumerate(lines):
        if 'LEAD RECOMMENDATION' in line:
            # Check if title is on the same line (after colon and signal ID)
            # Format: "## 🎯 LEAD RECOMMENDATION: SIGNAL_002"
            # Or: "LEAD RECOMMENDATION: Opportunity #1 — Some Title"
            # The real title is usually the NEXT line as a ### heading
            for j in range(i + 1, min(i + 4, len(lines))):
                next_line = lines[j].strip()
                if next_line.startswith('#'):
                    return next_line.lstrip('#').strip().replace('**', '')
                if len(next_line) > 20 and not next_line.startswith('---'):
                    return next_line.replace('**', '').strip()
            # Fallback: use whatever is after the colon on the LEAD RECOMMENDATION line
            after_colon = line.split(':', 1)[-1].strip() if ':' in line else ''
            if after_colon:
                return after_colon.replace('**', '').strip()
            break

    # Fallback: try RANK 1 heading
    rank_match = re.search(r'RANK 1[:\s]*(?:\*\*)?([^*\n]{10,})', text)
    if rank_match:
        return rank_match.group(1).replace('**', '').strip()

    # Last resort: first H3
    h3_match = re.search(r'^###\s+(.{15,})', text, re.MULTILINE)
    if h3_match:
        return h3_match.group(1).replace('**', '').strip()

    return "See discovery-brief.md"


def gate1_notify(verdict, avg_confidence, agent_scores, lead_opportunity):
    if "GO" in verdict and "NEEDS" not in verdict:
        emoji = "\u2705"
    elif "NEEDS_HUMAN_REVIEW" in verdict:
        emoji = "\u26a0\ufe0f"
    else:
        emoji = "\u274c"

    scores_text = ""
    for agent, score in agent_scores.items():
        s = float(score)
        if s >= 0.70:
            bar = "\U0001f7e2"
        elif s >= 0.40:
            bar = "\U0001f7e1"
        else:
            bar = "\U0001f534"
        scores_text += f"  {bar} {agent}: {score}\n"

    if not scores_text:
        scores_text = "  (no individual scores parsed)\n"

    message = (
        "<b>ProdAgentCo Gate 1 — Decision Required</b>\n\n"
        f"<b>VERDICT:</b> <code>{verdict}</code> {emoji}\n"
        f"<b>Average Confidence:</b> {avg_confidence}\n\n"
        f"<b>Lead Opportunity:</b> {lead_opportunity}\n\n"
        f"<b>Agent Scores:</b>\n{scores_text}\n"
        "<b>Your Options:</b>\n"
        "Reply <code>APPROVE</code> to proceed to Planning\n"
        "Reply <code>KILL</code> to archive\n"
        "Reply <code>DEFER</code> to add to backlog\n"
        "Reply <code>REVISE</code> to return to debate\n"
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

    # Verdict — handle "FINAL VERDICT:", "VERDICT:", "FINAL DECISION:" formats
    lower = verdict_text.lower()
    if "needs_human_review" in lower:
        result["verdict"] = "NEEDS_HUMAN_REVIEW"
    elif re.search(r'(?:verdict|decision)[:\s]*\*?\*?\s*go\b', lower) and "no-go" not in lower and "no go" not in lower:
        result["verdict"] = "GO"
    elif "no-go" in lower or "no go" in lower:
        result["verdict"] = "NO-GO"

    # Confidence — match "Average Confidence Score: 0.454" or "**Average Confidence Score: 0.688**"
    conf_match = re.search(r'[Aa]verage [Cc]onfidence [Ss]core[:\s]*\*{0,2}\s*(0\.\d+)', verdict_text)
    if not conf_match:
        # Fallback: "/ 5 = 0.64**"
        conf_match = re.search(r'/\s*\d+\s*=\s*(0\.\d+)', verdict_text)
    if conf_match:
        result["avg_confidence"] = float(conf_match.group(1))

    # Agent scores — match table rows with ** wrapped names and scores
    # Handles: | **CMO/PMF Analyst** | Role | **0.72** | BUILD |
    # And:     | Product Market Fit Agent | Role | **0.68** | BUILD |
    score_rows = re.findall(
        r'\|\s*\*?\*?([^|*]+?)\*?\*?\s*\|\s*[^|]+\|\s*\*?\*?([0-9]\.[0-9]+)\*?\*?\s*\|',
        verdict_text
    )
    for agent_name, score in score_rows:
        name = agent_name.strip()
        if not name or name.lower() in ("agent", "criterion", ""):
            continue
        result["agent_scores"][name] = score

    return result


def gate2_notify(planning_dir):
    """Send Gate 2 Telegram summary after Planning phase completes."""
    from pathlib import Path
    p = Path(planning_dir)

    # Extract key highlights from each brief
    brand_text = (p / "brand-brief.md").read_text() if (p / "brand-brief.md").exists() else ""
    prd_text = (p / "prd.md").read_text() if (p / "prd.md").exists() else ""
    tech_text = (p / "architecture-doc.md").read_text() if (p / "architecture-doc.md").exists() else ""
    fin_text = (p / "financial-model.md").read_text() if (p / "financial-model.md").exists() else ""

    # Product name — look for first name candidate
    name_match = re.search(r'(?:Name|#\d)[:\s]*\*?\*?([A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)?)\*?\*?', brand_text)
    product_name = name_match.group(1) if name_match else "TBD"

    # PRD headline — first H1 or H2
    prd_match = re.search(r'^#+\s*(.+)', prd_text, re.MULTILINE)
    prd_headline = prd_match.group(1).strip() if prd_match else "PRD complete"

    # Tech stack — look for stack/framework mentions
    tech_match = re.search(r'(?:Tech Stack|Technology Stack|Stack)[:\s]*\n((?:.*\n){1,5})', tech_text)
    tech_stack = tech_match.group(1).strip()[:200] if tech_match else "See architecture-doc.md"

    # Revenue projection
    rev_match = re.search(r'(?:revenue|ARR|projection)[^$]*(\$[\d,.]+[MKB]?\s*(?:ARR|revenue)?)', fin_text, re.IGNORECASE)
    revenue = rev_match.group(1).strip() if rev_match else "See financial-model.md"

    message = (
        "<b>ProdAgentCo Gate 2 — Planning Complete</b>\n\n"
        f"\U0001f3f7 <b>Product:</b> {product_name}\n"
        f"\U0001f4cb <b>PRD:</b> {prd_headline}\n"
        f"\U0001f527 <b>Tech:</b> {tech_stack}\n"
        f"\U0001f4b0 <b>Revenue Target:</b> {revenue}\n\n"
        "<b>7 deliverables ready:</b> PRD, Tech Spec, Financial Model, GTM Plan, Brand Brief, UX Brief, Legal Brief\n\n"
        "<b>Your Options:</b>\n"
        "Reply <code>APPROVE2</code> to proceed to Build\n"
        "Reply <code>REVISE2</code> to return to Planning\n"
    )
    success = send_telegram(message)
    if success:
        print("Gate 2 notification sent to Telegram")
    else:
        print("Failed to send Gate 2 notification")


def gate3_notify(build_dir):
    """Send Gate 3 Telegram summary after Build phase completes."""
    from pathlib import Path
    p = Path(build_dir)

    codebase_text = (p / "codebase.md").read_text() if (p / "codebase.md").exists() else ""
    qa_text = (p / "qa-report.md").read_text() if (p / "qa-report.md").exists() else ""
    security_text = (p / "security-report.md").read_text() if (p / "security-report.md").exists() else ""

    # Count files in codebase
    file_count = codebase_text.count("## ") if codebase_text else 0
    code_size = f"{len(codebase_text):,} chars"

    # QA verdict
    qa_match = re.search(r'(?:verdict|overall)[:\s]*\*?\*?(PASS|FAIL|CONDITIONAL)\*?\*?', qa_text, re.IGNORECASE)
    qa_verdict = qa_match.group(1).upper() if qa_match else "See qa-report.md"

    # QA score
    score_match = re.search(r'(?:quality score|score)[:\s]*\*?\*?(\d+(?:\.\d+)?)\s*(?:/\s*10)?', qa_text, re.IGNORECASE)
    qa_score = score_match.group(1) if score_match else "N/A"

    # Security rating
    sec_match = re.search(r'(?:risk rating|overall)[:\s]*\*?\*?(CRITICAL|HIGH|MEDIUM|LOW)\*?\*?', security_text, re.IGNORECASE)
    sec_rating = sec_match.group(1).upper() if sec_match else "See security-report.md"

    # Security findings count
    findings_count = len(re.findall(r'(?:CRITICAL|HIGH|MEDIUM|LOW)\s*\|', security_text, re.IGNORECASE))

    message = (
        "<b>ProdAgentCo Gate 3 — Build Complete</b>\n\n"
        f"\U0001f4e6 <b>Codebase:</b> ~{file_count} files, {code_size}\n"
        f"\u2705 <b>QA Verdict:</b> {qa_verdict} (score: {qa_score}/10)\n"
        f"\U0001f6e1 <b>Security:</b> {sec_rating} ({findings_count} findings)\n\n"
        "<b>3 deliverables ready:</b> Codebase, QA Report, Security Report\n\n"
        "<b>Your Options:</b>\n"
        "Reply <code>APPROVE3</code> to deploy to Vercel\n"
        "Reply <code>REVISE3</code> to re-run Build phase\n"
    )
    success = send_telegram(message)
    if success:
        print("Gate 3 notification sent to Telegram")
    else:
        print("Failed to send Gate 3 notification")
