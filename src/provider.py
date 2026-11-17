"""
Dhan API provider adapter for STAR Trading Scanner.
"""
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, List
import time

from .models import FuturesCandle, OptionChainSnapshot
from .config import (
    DHAN_API_KEY, DHAN_CLIENT_ID, API_TIMEOUT_SECONDS,
    API_RETRY_COUNT, API_RETRY_DELAY_SECONDS
)

logger = logging.getLogger(__name__)


class DhanAPIProvider:
    """Dhan API adapter for fetching market data."""
    
    BASE_URL = "https://api.dhan.co"
    
    def __init__(self):
        self.api_key = DHAN_API_KEY
        self.client_id = DHAN_CLIENT_ID
        self.timeout = API_TIMEOUT_SECONDS
        self.retry_count = API_RETRY_COUNT
        self.retry_delay = API_RETRY_DELAY_SECONDS
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def _retry_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """Execute request with retry logic."""
        for attempt in range(self.retry_count):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < self.retry_count - 1:
                    logger.warning(f"API request failed, retrying ({attempt + 1}/{self.retry_count}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"API request failed after {self.retry_count} attempts: {str(e)}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error in API request: {str(e)}")
                return None
        
        return None
    
    def get_futures_candle(
        self, symbol: str, expiry: str, timeframe: str = "5"
    ) -> Optional[FuturesCandle]:
        """
        Fetch the latest completed 5-minute futures candle for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            expiry: Expiry identifier (e.g., 'CUR')
            timeframe: Candle timeframe in minutes (default: 5)
        
        Returns:
            FuturesCandle object or None if error
        """
        try:
            # Construct security ID - format depends on Dhan API
            # This is a placeholder; actual format needs Dhan documentation
            security_id = f"{symbol}-FUT-{expiry}"
            
            url = f"{self.BASE_URL}/v1/quotes/intraday"
            params = {
                "securityId": security_id,
                "mode": "LTP",
                "exchangeTokens": f"{symbol}|{expiry}"
            }
            
            response = self._retry_request("GET", url, params=params)
            
            if not response or "data" not in response:
                logger.warning(f"No futures data received for {symbol} {expiry}")
                return None
            
            data = response["data"]
            
            candle = FuturesCandle(
                symbol=symbol,
                timestamp=datetime.fromisoformat(data.get("timestamp")),
                expiry=expiry,
                open_price=float(data.get("open", 0)),
                high_price=float(data.get("high", 0)),
                low_price=float(data.get("low", 0)),
                close_price=float(data.get("close", 0)),
                volume=float(data.get("volume", 0)),
                oi=float(data.get("oi", 0)),
                source_timestamp=datetime.now(),
                is_complete=data.get("isComplete", False),
            )
            
            return candle
        
        except Exception as e:
            logger.error(f"Error fetching futures candle for {symbol}: {str(e)}")
            return None
    
    def get_option_chain(
        self, symbol: str, expiry: str
    ) -> Optional[OptionChainSnapshot]:
        """
        Fetch current options chain data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            expiry: Expiry identifier (e.g., 'CUR')
        
        Returns:
            OptionChainSnapshot object or None if error
        """
        try:
            url = f"{self.BASE_URL}/v1/quotes/option_chain"
            params = {
                "symbol": symbol,
                "expiry": expiry,
                "mode": "FULL"
            }
            
            response = self._retry_request("GET", url, params=params)
            
            if not response or "data" not in response:
                logger.warning(f"No option chain data received for {symbol} {expiry}")
                return None
            
            data = response["data"]
            
            # Build strike dictionaries
            ce_oi = {}
            ce_volume = {}
            ce_iv = {}
            ce_bid_ask = {}
            
            pe_oi = {}
            pe_volume = {}
            pe_iv = {}
            pe_bid_ask = {}
            
            strikes = set()
            
            for chain_data in data.get("optionChain", []):
                strike = float(chain_data["strike"])
                strikes.add(strike)
                
                # CE side
                if "CE" in chain_data:
                    ce_data = chain_data["CE"]
                    ce_oi[strike] = float(ce_data.get("openInterest", 0))
                    ce_volume[strike] = float(ce_data.get("volume", 0))
                    ce_iv[strike] = float(ce_data.get("impliedVolatility", 0))
                    ce_bid_ask[strike] = (
                        float(ce_data.get("bid", 0)),
                        float(ce_data.get("ask", 0))
                    )
                
                # PE side
                if "PE" in chain_data:
                    pe_data = chain_data["PE"]
                    pe_oi[strike] = float(pe_data.get("openInterest", 0))
                    pe_volume[strike] = float(pe_data.get("volume", 0))
                    pe_iv[strike] = float(pe_data.get("impliedVolatility", 0))
                    pe_bid_ask[strike] = (
                        float(pe_data.get("bid", 0)),
                        float(pe_data.get("ask", 0))
                    )
            
            snapshot = OptionChainSnapshot(
                symbol=symbol,
                expiry=expiry,
                timestamp=datetime.now(),
                strikes=sorted(list(strikes)),
                ce_oi=ce_oi,
                ce_volume=ce_volume,
                ce_iv=ce_iv,
                ce_bid_ask=ce_bid_ask,
                pe_oi=pe_oi,
                pe_volume=pe_volume,
                pe_iv=pe_iv,
                pe_bid_ask=pe_bid_ask,
                underlying_price=float(data.get("underlyingPrice", 0)),
                futures_price=float(data.get("futuresPrice", None)) if "futuresPrice" in data else None,
                coverage_percent=float(data.get("coveragePercent", 100.0))
            )
            
            return snapshot
        
        except Exception as e:
            logger.error(f"Error fetching option chain for {symbol}: {str(e)}")
            return None
    
    def get_historical_candles(
        self, symbol: str, expiry: str, days_back: int = 5, timeframe: str = "5"
    ) -> List[FuturesCandle]:
        """
        Fetch historical futures candles for baseline calculations.
        
        Args:
            symbol: Stock symbol
            expiry: Expiry identifier
            days_back: Number of days to look back
            timeframe: Candle timeframe in minutes
        
        Returns:
            List of FuturesCandle objects
        """
        candles = []
        try:
            url = f"{self.BASE_URL}/v1/historical/candles"
            params = {
                "symbol": symbol,
                "expiry": expiry,
                "timeframe": timeframe,
                "daysBack": days_back
            }
            
            response = self._retry_request("GET", url, params=params)
            
            if not response or "data" not in response:
                logger.warning(f"No historical data received for {symbol}")
                return candles
            
            for candle_data in response["data"]:
                candle = FuturesCandle(
                    symbol=symbol,
                    timestamp=datetime.fromisoformat(candle_data.get("timestamp")),
                    expiry=expiry,
                    open_price=float(candle_data.get("open", 0)),
                    high_price=float(candle_data.get("high", 0)),
                    low_price=float(candle_data.get("low", 0)),
                    close_price=float(candle_data.get("close", 0)),
                    volume=float(candle_data.get("volume", 0)),
                    oi=float(candle_data.get("oi", 0)),
                    source_timestamp=datetime.now(),
                    is_complete=True
                )
                candles.append(candle)
        
        except Exception as e:
            logger.error(f"Error fetching historical candles for {symbol}: {str(e)}")
        
        return candles
    
    def test_connection(self) -> bool:
        """Test API connectivity and credentials."""
        try:
            url = f"{self.BASE_URL}/v1/user/account"
            response = self._retry_request("GET", url)
            return response is not None
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False
