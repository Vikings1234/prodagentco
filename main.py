#!/usr/bin/env python3
"""ProdAgentCo — Phase 1 entry point."""
from dotenv import load_dotenv
load_dotenv()

from pipelines.phase1 import run_discovery_phase

if __name__ == "__main__":
    print("🚀 ProdAgentCo Phase 1 — Discovery Cycle Starting...")
    result = run_discovery_phase()
    print("\n✅ Discovery complete. Check outputs/ for artifacts.")
    print(result)
