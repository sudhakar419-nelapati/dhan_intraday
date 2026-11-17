"""
Baseline calculation utilities for STAR Trading Scanner.
Computes historical baselines for volume and OI strength comparison.
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import logging

from .models import FuturesCandle
from .database import Database

logger = logging.getLogger(__name__)


class BaselineCalculator:
    """Calculate historical baselines for volume and OI metrics."""
    
    @staticmethod
    def _get_same_clock_slot_sessions(
        candles: List[FuturesCandle],
        lookback_sessions: int = 5
    ) -> List[List[FuturesCandle]]:
        """
        Group candles by same 5-minute clock slot across previous sessions.
        
        Args:
            candles: All available historical candles for a symbol
            lookback_sessions: Number of sessions to look back
        
        Returns:
            List of candle lists, one per previous session
        """
        if not candles:
            return []
        
        # Group candles by date
        sessions_by_date = {}
        for candle in candles:
            date_key = candle.timestamp.date()
            if date_key not in sessions_by_date:
                sessions_by_date[date_key] = []
            sessions_by_date[date_key].append(candle)
        
        # Sort by date; the current session (last candle's date) must not be part of its own baseline
        current_date = candles[-1].timestamp.date()
        sorted_dates = sorted((d for d in sessions_by_date if d != current_date), reverse=True)
        
        # Return candles for the most recent lookback_sessions
        result = []
        for date_key in sorted_dates[:lookback_sessions]:
            result.append(sessions_by_date[date_key])
        
        return result
    
    @staticmethod
    def calculate_volume_baseline(
        candles: List[FuturesCandle],
        lookback_sessions: int = 5
    ) -> Tuple[float, bool]:
        """
        Calculate average 5-minute volume baseline.
        
        Strategy: Use same 5-minute clock slot from previous 5 valid trading sessions.
        
        Args:
            candles: Historical candles for a symbol
            lookback_sessions: Number of sessions to look back
        
        Returns:
            (average_volume, is_sufficient) where is_sufficient indicates
            if at least 3 valid observations exist
        """
        if not candles or len(candles) < 2:
            return 0, False
        
        # Get current candle's time slot
        current_slot_time = candles[-1].timestamp.time()
        
        # Collect same time slot volumes from previous sessions
        slot_volumes = []
        
        sessions = BaselineCalculator._get_same_clock_slot_sessions(candles, lookback_sessions)
        
        for session_candles in sessions:
            # Find candle matching the current time slot
            for candle in session_candles:
                if candle.timestamp.time() == current_slot_time:
                    slot_volumes.append(candle.volume)
                    break
        
        # Need at least 3 observations
        is_sufficient = len(slot_volumes) >= 3
        
        if is_sufficient:
            avg_volume = sum(slot_volumes) / len(slot_volumes)
            return avg_volume, True
        else:
            return 0, False
    
    @staticmethod
    def calculate_oi_strength_baseline(
        candles: List[FuturesCandle],
        lookback_sessions: int = 5
    ) -> Tuple[float, bool]:
        """
        Calculate average OI change baseline for strength comparison.
        
        Strategy: Use same 5-minute clock slot from previous 5 valid trading sessions.
        
        Args:
            candles: Historical candles for a symbol (must be in chronological order)
            lookback_sessions: Number of sessions to look back
        
        Returns:
            (average_oi_change, is_sufficient) where average_oi_change is the
            absolute value of average OI change, and is_sufficient indicates
            if at least 3 valid observations exist
        """
        if not candles or len(candles) < 2:
            return 0, False
        
        # Get current candle's time slot
        current_slot_time = candles[-1].timestamp.time()
        
        # Collect same time slot OI changes from previous sessions
        slot_oi_changes = []
        
        sessions = BaselineCalculator._get_same_clock_slot_sessions(candles, lookback_sessions)
        
        for session_candles in sessions:
            # Find candle matching the current time slot
            for i, candle in enumerate(session_candles):
                if candle.timestamp.time() == current_slot_time and i > 0:
                    prev_candle = session_candles[i - 1]
                    oi_change = abs(candle.oi - prev_candle.oi)
                    slot_oi_changes.append(oi_change)
                    break
        
        # Need at least 3 observations
        is_sufficient = len(slot_oi_changes) >= 3
        
        if is_sufficient:
            avg_oi_change = sum(slot_oi_changes) / len(slot_oi_changes)
            return avg_oi_change, True
        else:
            return 0, False
    
    @staticmethod
    def calculate_volume_rank(
        current_volume: float,
        all_session_volumes: List[float]
    ) -> int:
        """
        Rank current candle's volume among all candles in this session.
        
        Args:
            current_volume: Volume of current candle
            all_session_volumes: All volumes from current session so far
        
        Returns:
            Rank (#1 is highest volume in session)
        """
        if not all_session_volumes:
            return 999
        
        # Sort volumes in descending order
        sorted_volumes = sorted(all_session_volumes, reverse=True)
        
        # Find rank (1-based)
        try:
            rank = sorted_volumes.index(current_volume) + 1
            return rank
        except ValueError:
            # Volume not found in list (shouldn't happen, but handle gracefully)
            return len(sorted_volumes)


class BaselineStatusChecker:
    """Check if baseline data is sufficient for reliable calculations."""
    
    @staticmethod
    def check_volume_baseline(is_sufficient: bool, lookback_sessions: int = 5) -> str:
        """Return status indicator for volume baseline."""
        if is_sufficient:
            return f"Valid ({lookback_sessions} sessions)"
        else:
            return f"INSUFFICIENT BASELINE ({lookback_sessions} sessions required)"
    
    @staticmethod
    def check_oi_baseline(is_sufficient: bool, lookback_sessions: int = 5) -> str:
        """Return status indicator for OI baseline."""
        if is_sufficient:
            return f"Valid ({lookback_sessions} sessions)"
        else:
            return f"INSUFFICIENT BASELINE ({lookback_sessions} sessions required)"
