"""Dhan v2 API adapter for STAR Trading Scanner (real endpoints)."""
import logging
import threading
import time
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional

import pandas as pd
import requests

from .config import (API_RETRY_COUNT, API_RETRY_DELAY_SECONDS, API_TIMEOUT_SECONDS,
                     DATA_DIR, get_client_id, get_token)
from .models import FuturesCandle, OptionChainSnapshot

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))
MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
_GAP = {"intraday": 0.3, "chain": 3.1}          # seconds between calls (Dhan limits)
_last: Dict[str, float] = {}
_lock = threading.Lock()


class DhanAPIProvider:
    BASE_URL = "https://api.dhan.co/v2"

    def __init__(self):
        self.session = requests.Session()
        self._futs: Optional[pd.DataFrame] = None
        self.last_error: Optional[str] = None

    # ---- plumbing -------------------------------------------------------
    def _headers(self):
        return {"access-token": get_token(), "client-id": get_client_id(),
                "Content-Type": "application/json", "Accept": "application/json"}

    def _post(self, path: str, body: dict, kind: str):
        """POST with rate-limit spacing and retry. Returns parsed JSON or None (error in last_error)."""
        if not get_token() or not get_client_id():
            self.last_error = "Token or client id missing"
            return None
        for attempt in range(1, API_RETRY_COUNT + 1):
            with _lock:
                wait = _GAP[kind] - (time.monotonic() - _last.get(kind, 0))
                if wait > 0:
                    time.sleep(wait)
                try:
                    r = self.session.post(self.BASE_URL + path, json=body, headers=self._headers(),
                                          timeout=API_TIMEOUT_SECONDS)
                except requests.RequestException as e:
                    r = None
                    self.last_error = f"network error: {type(e).__name__}"
                finally:
                    _last[kind] = time.monotonic()
            if r is not None:
                if r.status_code == 200:
                    self.last_error = None
                    return r.json()
                self.last_error = f"HTTP {r.status_code}: {r.text[:200]}"
                if r.status_code in (400, 401, 403):       # retrying will not help
                    return None
            time.sleep(API_RETRY_DELAY_SECONDS * attempt)
        logger.error("%s failed: %s", path, self.last_error)
        return None

    # ---- instrument lookup ----------------------------------------------
    def _futures_table(self) -> pd.DataFrame:
        """symbol -> current-month stock future id, underlying (cash) id, lot, expiry."""
        if self._futs is not None:
            return self._futs
        cache = DATA_DIR / f"fut_{date.today()}.csv"
        if cache.exists():
            self._futs = pd.read_csv(cache)
            return self._futs
        m = pd.read_csv(MASTER_URL, low_memory=False)
        nse = m[m["EXCH_ID"] == "NSE"]
        fut = nse[nse["INSTRUMENT"] == "FUTSTK"].copy()
        fut["expiry"] = pd.to_datetime(fut["SM_EXPIRY_DATE"], errors="coerce").dt.date
        fut = fut[fut["expiry"] >= date.today()]
        fut = fut[fut["expiry"] == fut["expiry"].min()].drop_duplicates("UNDERLYING_SYMBOL")
        eq = nse[(nse["INSTRUMENT"] == "EQUITY") & (nse["SERIES"] == "EQ")]
        eq_map = dict(zip(eq["UNDERLYING_SYMBOL"], eq["SECURITY_ID"]))
        t = pd.DataFrame({
            "symbol": fut["UNDERLYING_SYMBOL"].values,
            "fut_id": fut["SECURITY_ID"].astype(int).values,
            "eq_id": [int(eq_map.get(s, u)) for s, u in zip(fut["UNDERLYING_SYMBOL"],
                                                           fut["UNDERLYING_SECURITY_ID"])],
            "lot": fut["LOT_SIZE"].astype(int).values,
            "expiry": fut["expiry"].astype(str).values,
        })
        t.to_csv(cache, index=False)
        self._futs = t
        return t

    def instrument(self, symbol: str) -> Optional[dict]:
        t = self._futures_table()
        row = t[t["symbol"] == symbol.upper()]
        return None if row.empty else row.iloc[0].to_dict()

    # ---- market data ----------------------------------------------------
    def get_historical_candles(self, symbol: str, days_back: int = 7,
                               timeframe: str = "5") -> List[FuturesCandle]:
        """5-minute candles (with OI) of the current-month future, oldest first,
        completed candles only. Timestamps are naive IST (start of candle)."""
        ins = self.instrument(symbol)
        if not ins:
            self.last_error = f"{symbol} has no current-month stock future"
            return []
        now = datetime.now(IST)
        body = {"securityId": str(ins["fut_id"]), "exchangeSegment": "NSE_FNO",
                "instrument": "FUTSTK", "interval": timeframe, "oi": True,
                "fromDate": (now - timedelta(days=days_back)).strftime("%Y-%m-%d %H:%M:%S"),
                "toDate": now.strftime("%Y-%m-%d %H:%M:%S")}
        reply = self._post("/charts/intraday", body, "intraday")
        if not reply:
            return []
        d = reply.get("data") if isinstance(reply.get("data"), dict) else reply
        need = ("timestamp", "open", "high", "low", "close", "volume")
        if not all(k in d for k in need) or not d["timestamp"]:
            return []
        oi = d.get("open_interest") or [0] * len(d["timestamp"])
        out, cutoff = [], now.replace(tzinfo=None)
        for i, ts in enumerate(d["timestamp"]):
            start = datetime.fromtimestamp(ts, IST).replace(tzinfo=None)
            if start + timedelta(minutes=int(timeframe)) > cutoff:      # still forming
                continue
            out.append(FuturesCandle(
                symbol=symbol.upper(), timestamp=start, expiry=str(ins["expiry"]),
                open_price=float(d["open"][i]), high_price=float(d["high"][i]),
                low_price=float(d["low"][i]), close_price=float(d["close"][i]),
                volume=float(d["volume"][i]), oi=float(oi[i] or 0)))
        out.sort(key=lambda c: c.timestamp)
        return out

    def get_futures_candle(self, symbol: str, expiry: str = "", timeframe: str = "5"
                           ) -> Optional[FuturesCandle]:
        c = self.get_historical_candles(symbol, days_back=3, timeframe=timeframe)
        return c[-1] if c else None

    def get_option_chain(self, symbol: str, expiry: str = "") -> Optional[OptionChainSnapshot]:
        ins = self.instrument(symbol)
        if not ins:
            return None
        reply = self._post("/optionchain", {"UnderlyingScrip": int(ins["eq_id"]),
                                            "UnderlyingSeg": "NSE_EQ",
                                            "Expiry": expiry or str(ins["expiry"])}, "chain")
        data = (reply or {}).get("data") or {}
        oc = data.get("oc") or {}
        if not oc:
            return None
        s = {k: {} for k in ("ce_oi", "ce_volume", "ce_iv", "ce_bid_ask",
                             "pe_oi", "pe_volume", "pe_iv", "pe_bid_ask")}
        for strike_s, legs in oc.items():
            strike = float(strike_s)
            for side in ("ce", "pe"):
                o = legs.get(side)
                if not o:
                    continue
                s[f"{side}_oi"][strike] = float(o.get("oi") or 0)
                s[f"{side}_volume"][strike] = float(o.get("volume") or 0)
                s[f"{side}_iv"][strike] = float(o.get("implied_volatility") or 0)
                s[f"{side}_bid_ask"][strike] = (float(o.get("top_bid_price") or 0),
                                                float(o.get("top_ask_price") or 0))
        return OptionChainSnapshot(symbol=symbol.upper(), expiry=str(ins["expiry"]),
                                   timestamp=datetime.now(), strikes=sorted(float(k) for k in oc),
                                   underlying_price=float(data.get("last_price") or 0), **s)

    def test_connection(self) -> bool:
        if not get_token() or not get_client_id():
            self.last_error = "Token or client id missing"
            return False
        try:
            r = self.session.get(self.BASE_URL + "/profile", headers=self._headers(),
                                 timeout=API_TIMEOUT_SECONDS)
        except requests.RequestException as e:
            self.last_error = f"network error: {type(e).__name__}"
            return False
        if r.status_code != 200:
            self.last_error = f"HTTP {r.status_code}: {r.text[:200]}"
        return r.status_code == 200
