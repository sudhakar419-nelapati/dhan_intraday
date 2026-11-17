"""
Configuration management for STAR Trading Scanner.
Loads from environment variables, .env file, or Streamlit secrets.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file (for local development)
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# API Configuration - Support both local and Streamlit Cloud
try:
    # Try Streamlit secrets (for Streamlit Cloud deployment)
    import streamlit as st
    DHAN_API_KEY = st.secrets.get("DHAN_API_KEY", os.getenv("DHAN_API_KEY", ""))
    DHAN_CLIENT_ID = st.secrets.get("DHAN_CLIENT_ID", os.getenv("DHAN_CLIENT_ID", ""))
except:
    # Fallback to environment variables (for local development)
    DHAN_API_KEY = os.getenv("DHAN_API_KEY", "")
    DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "")

# Database Configuration
DB_PATH = os.getenv("DB_PATH", "./data/scanner.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Session Times (IST)
SESSION_START_TIME = os.getenv("SESSION_START_TIME", "09:15")
SESSION_END_TIME = os.getenv("SESSION_END_TIME", "15:30")

# Price and Volume Thresholds
PRICE_NOISE_THRESHOLD = float(os.getenv("PRICE_NOISE_THRESHOLD", "0.0001"))
VOLUME_RANK_STRONG = int(os.getenv("VOLUME_RANK_STRONG", "100"))
VOLUME_RANK_MODERATE = int(os.getenv("VOLUME_RANK_MODERATE", "250"))
VOLUME_RANK_WARNING = int(os.getenv("VOLUME_RANK_WARNING", "300"))

# OI Strength Thresholds
OI_STRENGTH_WEAK = float(os.getenv("OI_STRENGTH_WEAK", "1.0"))
OI_STRENGTH_MEDIUM_LOW = float(os.getenv("OI_STRENGTH_MEDIUM_LOW", "1.4"))
OI_STRENGTH_STRONG = float(os.getenv("OI_STRENGTH_STRONG", "1.4"))

# Baseline Configuration
BASELINE_LOOKBACK_SESSIONS = int(os.getenv("BASELINE_LOOKBACK_SESSIONS", "5"))
NEUTRAL_BAND = float(os.getenv("NEUTRAL_BAND", "0.0"))

# Universe Symbols
UNIVERSE_SYMBOLS = os.getenv(
    "UNIVERSE_SYMBOLS",
    "RELIANCE,TCS,INFY,HDFC,ICICIBANK,AXISBANK,LT,WIPRO,MARUTI"
).split(",")

# API Configuration
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "10"))
API_RETRY_COUNT = int(os.getenv("API_RETRY_COUNT", "3"))
API_RETRY_DELAY_SECONDS = int(os.getenv("API_RETRY_DELAY_SECONDS", "2"))
MAX_CONCURRENT_SYMBOLS = int(os.getenv("MAX_CONCURRENT_SYMBOLS", "5"))

# Data Quality
MIN_OPTIONS_COVERAGE_PERCENT = int(os.getenv("MIN_OPTIONS_COVERAGE_PERCENT", "80"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_PATH = os.getenv("LOG_PATH", "./logs")
Path(LOG_PATH).mkdir(parents=True, exist_ok=True)

# Feature Flags
PAPER_MODE = os.getenv("PAPER_MODE", "false").lower() == "true"
ENABLE_HISTORICAL_REPLAY = os.getenv("ENABLE_HISTORICAL_REPLAY", "false").lower() == "true"


def validate_config():
    """Validate critical configuration parameters."""
    errors = []
    
    if not DHAN_API_KEY or DHAN_API_KEY == "your_dhan_api_key_here":
        errors.append("DHAN_API_KEY not configured properly")
    
    if not DHAN_CLIENT_ID or DHAN_CLIENT_ID == "your_dhan_client_id_here":
        errors.append("DHAN_CLIENT_ID not configured properly")
    
    if not UNIVERSE_SYMBOLS:
        errors.append("UNIVERSE_SYMBOLS is empty")
    
    if errors:
        logging.warning("Configuration warnings: " + "; ".join(errors))
        return False
    
    return True


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    if not logger.handlers:
        handler = logging.FileHandler(f"{LOG_PATH}/{name}.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
