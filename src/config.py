"""Configuration for STAR Trading Scanner. Reads environment variables / .env / config/.env."""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
# Works whether the file sits in the project root, in config/, or in src/.
for _f in (ROOT / "config" / ".env", ROOT / ".env", ROOT / "src" / ".env"):
    if _f.exists():
        load_dotenv(_f)


def _first(*names, default=""):
    for n in names:
        v = os.getenv(n)
        if v:
            return v.strip().strip('"').strip("'")
    return default


def get_token() -> str:
    """Read at call time so a token pasted in the dashboard is picked up."""
    return _first("DHAN_ACCESS_TOKEN", "DHAN_API_KEY", "ACCESS_TOKEN")


def get_client_id() -> str:
    return _first("DHAN_CLIENT_ID", "CLIENT_ID")


DB_PATH = os.getenv("DB_PATH", str(ROOT / "data" / "scanner.db"))
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

SESSION_START_TIME = os.getenv("SESSION_START_TIME", "09:15")
SESSION_END_TIME = os.getenv("SESSION_END_TIME", "15:30")

PRICE_NOISE_THRESHOLD = float(os.getenv("PRICE_NOISE_THRESHOLD", "0.0001"))
VOLUME_RANK_STRONG = int(os.getenv("VOLUME_RANK_STRONG", "100"))
VOLUME_RANK_MODERATE = int(os.getenv("VOLUME_RANK_MODERATE", "250"))
VOLUME_RANK_WARNING = int(os.getenv("VOLUME_RANK_WARNING", "300"))

OI_STRENGTH_WEAK = float(os.getenv("OI_STRENGTH_WEAK", "1.0"))
OI_STRENGTH_MEDIUM_LOW = float(os.getenv("OI_STRENGTH_MEDIUM_LOW", "1.0"))
OI_STRENGTH_STRONG = float(os.getenv("OI_STRENGTH_STRONG", "1.4"))

BASELINE_LOOKBACK_SESSIONS = int(os.getenv("BASELINE_LOOKBACK_SESSIONS", "5"))
NEUTRAL_BAND = float(os.getenv("NEUTRAL_BAND", "0.0"))

# HDFC no longer trades as a stock future (merged into HDFCBANK).
UNIVERSE_SYMBOLS = [s.strip().upper() for s in os.getenv(
    "UNIVERSE_SYMBOLS",
    "RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK,AXISBANK,LT,WIPRO,MARUTI",
).split(",") if s.strip()]

API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "20"))
API_RETRY_COUNT = int(os.getenv("API_RETRY_COUNT", "3"))
API_RETRY_DELAY_SECONDS = int(os.getenv("API_RETRY_DELAY_SECONDS", "2"))
MIN_OPTIONS_COVERAGE_PERCENT = int(os.getenv("MIN_OPTIONS_COVERAGE_PERCENT", "80"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_PATH = os.getenv("LOG_PATH", str(ROOT / "logs"))
Path(LOG_PATH).mkdir(parents=True, exist_ok=True)


def validate_config() -> bool:
    errors = []
    if not get_token():
        errors.append("access token missing (DHAN_ACCESS_TOKEN)")
    if not get_client_id():
        errors.append("DHAN_CLIENT_ID missing")
    if errors:
        logging.warning("Configuration warnings: " + "; ".join(errors))
        return False
    return True


def get_logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(LOG_LEVEL)
    if not log.handlers:
        h = logging.FileHandler(f"{LOG_PATH}/{name.split('.')[-1]}.log")
        h.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        log.addHandler(h)
    return log
