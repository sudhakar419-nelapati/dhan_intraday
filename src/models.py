"""
Data models for STAR Trading Scanner.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class FuturesCandle:
    """5-minute futures candle data."""
    symbol: str
    timestamp: datetime
    expiry: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    oi: float
    source_timestamp: datetime = field(default_factory=datetime.now)
    is_complete: bool = True
    error_message: Optional[str] = None


@dataclass
class Gate7Result:
    """Gate 7 - Futures Read analysis result."""
    symbol: str
    expiry: str
    candle_timestamp: datetime
    
    # Price metrics
    price_direction: str  # UP, DOWN, FLAT
    price_change_percent: float
    
    # OI metrics
    oi_change: float
    oi_change_percent: float
    
    # Volume metrics
    futures_volume: float
    futures_volume_percent: float
    
    # Strength metrics
    oi_strength: float
    volume_strength: float
    volume_rank: int
    
    # Classification
    direction_label: str  # Fresh Long Build, Short Covering, Fresh Short Build, Long Unwinding, Neutral/Unclassified
    bias: str  # Bullish/CE, Bearish/PE, Neutral
    
    # Quality indicators
    is_reliable: bool
    signal_strength: str  # weak, medium, strong
    
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class Gate8Result:
    """Gate 8 - Futures Neutralization analysis result."""
    symbol: str
    expiry: str
    session_date: datetime
    
    # Accumulation buckets (from start of session 09:15 IST)
    fresh_long_fl: float  # Price UP + OI UP
    short_covering_sc: float  # Price UP + OI DOWN
    fresh_short_fs: float  # Price DOWN + OI UP
    long_unwinding_lu: float  # Price DOWN + OI DOWN
    
    # Scores
    bull_score: float  # FL + SC
    bear_score: float  # FS + LU
    net_lead: float  # Bull Score - Bear Score
    
    # Classification
    lead_label: str  # BULL LEAD, BEAR LEAD, NEUTRAL
    ce_alignment: bool  # requires BULL LEAD
    pe_alignment: bool  # requires BEAR LEAD
    
    # Data quality
    candle_count: int
    last_candle_timestamp: datetime
    
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class OptionChainSnapshot:
    """Options chain data snapshot."""
    symbol: str
    expiry: str
    timestamp: datetime
    
    # By strike
    strikes: List[float]
    ce_oi: dict  # strike -> OI
    ce_volume: dict  # strike -> volume
    ce_iv: dict  # strike -> IV
    ce_bid_ask: dict  # strike -> (bid, ask)
    
    pe_oi: dict
    pe_volume: dict
    pe_iv: dict
    pe_bid_ask: dict
    
    # Overall metrics
    underlying_price: float
    futures_price: Optional[float] = None
    source_timestamp: datetime = field(default_factory=datetime.now)
    coverage_percent: float = 100.0
    error_message: Optional[str] = None


@dataclass
class GateChecklistResult:
    """Complete Gate 1-8 evaluation for one side (CE or PE)."""
    symbol: str
    expiry: str
    side: str  # CE or PE
    gate_results: dict  # gate_number -> (status: PASS/FAIL/WEAK/OPPOSITE/DATA_MISSING, reason: str)
    pass_count: int
    readiness_status: str  # Full-quantity, Half-quantity, Wait, Stay out
    readiness_description: str
    
    # Optional fields with defaults
    total_gates: int = 8
    first_failed_gate: Optional[int] = None
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScannerRowData:
    """Single row in market-wide scanner table."""
    symbol: str
    rank: int
    ce_readiness_pass_count: int
    ce_readiness_status: str
    pe_readiness_pass_count: int
    pe_readiness_status: str
    
    # Gate 7 details
    gate7_price_direction: str
    gate7_price_change_percent: float
    gate7_oi_change: float
    gate7_oi_change_percent: float
    gate7_futures_volume: float
    gate7_futures_volume_percent: float
    gate7_direction_label: str
    gate7_oi_strength: float
    gate7_volume_strength: float
    gate7_volume_rank: int
    
    # Gate 8 details
    gate8_bull_score: float
    gate8_bear_score: float
    gate8_net_lead: float
    gate8_lead_label: str
    
    # Data quality
    data_quality: str  # Fresh, Stale, Missing
    candle_timestamp: datetime
    options_coverage_percent: float
    
    # Optional existing columns
    buy_contract: Optional[str] = None
    premium: Optional[float] = None
    lot_cost: Optional[float] = None
    iv: Optional[float] = None
    opt_lots: Optional[int] = None
    
    last_refresh: datetime = field(default_factory=datetime.now)
