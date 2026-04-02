#!/usr/bin/env python3
"""ProdAgentCo — Phase 1 entry point."""
import sys
from dotenv import load_dotenv
load_dotenv()

from pipelines.phase1 import run_discovery_phase
from pipelines.debate import run_debate_phase
from gates.hitl_gates import gate1_notify, gate1_parse_verdict
from config.settings import OUTPUT_DIR, DEBATE_CONFIDENCE_THRESHOLD
import subprocess
import datetime

def commit_and_push_outputs():
    """Silently commit and push the outputs/ folder to GitHub."""
    try:
        # Run git add outputs/
        subprocess.run(['git', 'add', 'outputs/'], check=True, capture_output=True)
        
        # Get timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Run git commit
        commit_msg = f"Pipeline run — {timestamp}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True)
        
        # Run git push
        subprocess.run(['git', 'push'], check=True, capture_output=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        print(f"Error output: {e.stderr.decode() if e.stderr else 'None'}")

if __name__ == "__main__":
    # Accept domain and custom query from CLI: python main.py <domain> [custom_query]
    domain = sys.argv[1] if len(sys.argv) > 1 else "agentic-payments"
    custom_query = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"🚀 ProdAgentCo Phase 1 — Discovery Cycle Starting (domain: {domain})...")
    discovery_result = run_discovery_phase(domain=domain, custom_query=custom_query)

    output_file = OUTPUT_DIR / "discovery-brief.md"
    with open(output_file, "w") as f:
        f.write(str(discovery_result))
    print(f"\n✅ Discovery complete. Brief saved to {output_file}")

    print("\n🎯 Starting CEO Debate Phase...")
    debate_result = run_debate_phase()

    verdict_file = OUTPUT_DIR / "debate-verdict.md"
    with open(verdict_file, "w") as f:
        f.write(str(debate_result))
    print(f"\n✅ Debate complete. Verdict saved to {verdict_file}")

    # Commit and push outputs to GitHub
    commit_and_push_outputs()

    # Parse real verdict and fire Gate 1 if needed
    parsed = gate1_parse_verdict(str(debate_result))
    avg_conf = parsed["avg_confidence"]
    verdict = parsed["verdict"]

    print(f"\n📊 CEO Verdict: {verdict} | Avg Confidence: {avg_conf}")

    if verdict != "GO" or avg_conf < DEBATE_CONFIDENCE_THRESHOLD:
        print("📱 Firing Gate 1 HITL notification...")

        # Extract lead opportunity title from discovery brief
        brief_path = OUTPUT_DIR / "discovery-brief.md"
        lead_opp = "See discovery-brief.md"
        if brief_path.exists():
            import re as _re
            brief_text = brief_path.read_text()
            title_match = (_re.search(r'RANK 1[:\s]*(?:\*\*)?([^*\n]+)', brief_text)
                or _re.search(r'LEAD RECOMMENDATION[:\s]*(?:Opportunity #\d+\s*—?\s*)?(.+)', brief_text))
            if title_match:
                lead_opp = title_match.group(1).replace('**', '').strip()

        gate1_notify(
            verdict=verdict,
            avg_confidence=avg_conf,
            lead_opportunity=lead_opp,
            agent_scores=parsed.get("agent_scores", {})
        )
    else:
        print("✅ CEO confidence above threshold — proceeding autonomously to Planning")
