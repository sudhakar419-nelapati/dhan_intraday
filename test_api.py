"""Quick check: python test_api.py  (needs DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN in .env)."""
from src.config import get_client_id, get_token
from src.provider import DhanAPIProvider

p = DhanAPIProvider()
print("credentials:", bool(get_client_id()), bool(get_token()))
print("profile:", "OK" if p.test_connection() else f"FAILED {p.last_error}")
for s in ("RELIANCE", "TCS"):
    c = p.get_historical_candles(s, 5)
    print(s, len(c), "candles", (c[-1].timestamp, c[-1].close_price, c[-1].oi) if c else p.last_error)
