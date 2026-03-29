import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

ICE_THRESHOLD = 200
DEBATE_CONFIDENCE_THRESHOLD = 0.70
DEBATE_MIN_CONFIDENCE = 0.40

PER_RUN_BUDGET_USD = float(os.getenv("PER_RUN_BUDGET_USD", "5.00"))
CFO_ALERT_THRESHOLD = float(os.getenv("CFO_ALERT_THRESHOLD", "0.70"))
CFO_HARD_STOP = float(os.getenv("CFO_HARD_STOP", "0.95"))
