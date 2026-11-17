"""
Unit tests for Gate 7 and Gate 8 calculations.
Tests the STAR Trading Scanner gate evaluation logic.
"""
import pytest
from datetime import datetime
from src.models import FuturesCandle, Gate7Result, Gate8Result
from src.gates import Gate7Calculator, Gate8Calculator, GatesCalculator


class TestGate7Calculator:
    """Test Gate 7: Futures Read analysis."""
    
    def test_direction_classification_fresh_long_build(self):
        """Test classification: Close UP, OI UP = Fresh Long Build (CE bias)."""
        label, bias = Gate7Calculator._classify_direction("UP", "UP")
        assert label == "Fresh Long Build"
        assert bias == "Bullish / CE"
    
    def test_direction_classification_short_covering(self):
        """Test classification: Close UP, OI DOWN = Short Covering (CE bias)."""
        label, bias = Gate7Calculator._classify_direction("UP", "DOWN")
        assert label == "Short Covering"
        assert bias == "Bullish / CE"
    
    def test_direction_classification_fresh_short_build(self):
        """Test classification: Close DOWN, OI UP = Fresh Short Build (PE bias)."""
        label, bias = Gate7Calculator._classify_direction("DOWN", "UP")
        assert label == "Fresh Short Build"
        assert bias == "Bearish / PE"
    
    def test_direction_classification_long_unwinding(self):
        """Test classification: Close DOWN, OI DOWN = Long Unwinding (PE bias)."""
        label, bias = Gate7Calculator._classify_direction("DOWN", "DOWN")
        assert label == "Long Unwinding"
        assert bias == "Bearish / PE"
    
    def test_direction_classification_flat_price_neutral(self):
        """Test classification: Close FLAT = Neutral."""
        label, bias = Gate7Calculator._classify_direction("FLAT", "UP")
        assert "Neutral" in label
        assert bias == "Neutral"
    
    def test_signal_strength_weak(self):
        """Test signal strength: OI strength < 1.0x = weak."""
        strength = Gate7Calculator._get_signal_strength(0.8, 150)
        assert strength == "weak"
    
    def test_signal_strength_medium(self):
        """Test signal strength: OI strength 1.0x-1.4x = medium."""
        strength = Gate7Calculator._get_signal_strength(1.2, 150)
        assert strength == "medium"
    
    def test_signal_strength_strong(self):
        """Test signal strength: OI strength > 1.4x = strong."""
        strength = Gate7Calculator._get_signal_strength(1.5, 150)
        assert strength == "strong"
    
    def test_reliability_oi_strength_weak(self):
        """Test reliability: OI strength < 1.0x = unreliable."""
        is_reliable = Gate7Calculator._is_reliable(0.8, 150)
        assert is_reliable is False
    
    def test_reliability_volume_rank_high(self):
        """Test reliability: Volume rank > 300 = unreliable."""
        is_reliable = Gate7Calculator._is_reliable(1.5, 310)
        assert is_reliable is False
    
    def test_reliability_valid_parameters(self):
        """Test reliability: Valid OI and volume = reliable."""
        is_reliable = Gate7Calculator._is_reliable(1.5, 100)
        assert is_reliable is True
    
    def test_calculate_gate7_missing_data(self):
        """Test AT-01: Handle missing previous candle gracefully."""
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime.now(),
            expiry="CUR", open_price=100, high_price=102,
            low_price=99, close_price=101, volume=1000, oi=5000
        )
        
        result = Gate7Calculator.calculate(current, None, 1000, 50, 100)
        
        assert result.direction_label == "DATA MISSING"
        assert result.is_reliable is False
    
    def test_calculate_gate7_fresh_long_build(self):
        """Test AT-01: Close rises and OI rises = Fresh Long Build."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100,
            low_price=100, close_price=100, volume=1000, oi=5000
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=102,
            low_price=100, close_price=101, volume=1200, oi=5500
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.price_direction == "UP"
        assert result.oi_change > 0
        assert result.direction_label == "Fresh Long Build"
        assert result.bias == "Bullish / CE"
    
    def test_calculate_gate7_short_covering(self):
        """Test AT-02: Close rises and OI falls = Short Covering."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100,
            low_price=100, close_price=100, volume=1000, oi=5000
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=102,
            low_price=100, close_price=101, volume=1200, oi=4500
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.price_direction == "UP"
        assert result.oi_change < 0
        assert result.direction_label == "Short Covering"
        assert result.bias == "Bullish / CE"
    
    def test_calculate_gate7_fresh_short_build(self):
        """Test AT-03: Close falls and OI rises = Fresh Short Build."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100,
            low_price=100, close_price=100, volume=1000, oi=5000
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=100,
            low_price=98, close_price=99, volume=1200, oi=5500
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.price_direction == "DOWN"
        assert result.oi_change > 0
        assert result.direction_label == "Fresh Short Build"
        assert result.bias == "Bearish / PE"
    
    def test_calculate_gate7_long_unwinding(self):
        """Test AT-04: Close falls and OI falls = Long Unwinding."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100,
            low_price=100, close_price=100, volume=1000, oi=5000
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=100,
            low_price=98, close_price=99, volume=1200, oi=4500
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.price_direction == "DOWN"
        assert result.oi_change < 0
        assert result.direction_label == "Long Unwinding"
        assert result.bias == "Bearish / PE"
    
    def test_calculate_gate7_flat_or_missing(self):
        """Test AT-05: Price flat or OI missing = Neutral."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100,
            low_price=100, close_price=100, volume=1000, oi=0
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=100,
            low_price=100, close_price=100, volume=1200, oi=0
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.price_direction == "FLAT"
        assert "Neutral" in result.direction_label
        assert result.bias == "Neutral"


class TestGate8Calculator:
    """Test Gate 8: Futures Neutralization analysis."""
    
    def test_classify_candle_fresh_long(self):
        """Test candle classification: UP + UP = FL."""
        classification = Gate8Calculator._classify_candle("UP", "UP")
        assert classification == "FL"
    
    def test_classify_candle_short_covering(self):
        """Test candle classification: UP + DOWN = SC."""
        classification = Gate8Calculator._classify_candle("UP", "DOWN")
        assert classification == "SC"
    
    def test_classify_candle_fresh_short(self):
        """Test candle classification: DOWN + UP = FS."""
        classification = Gate8Calculator._classify_candle("DOWN", "UP")
        assert classification == "FS"
    
    def test_classify_candle_long_unwinding(self):
        """Test candle classification: DOWN + DOWN = LU."""
        classification = Gate8Calculator._classify_candle("DOWN", "DOWN")
        assert classification == "LU"
    
    def test_accumulate_session_empty(self):
        """Test accumulation with no candles."""
        result = Gate8Calculator.accumulate_session([])
        
        assert result.fresh_long_fl == 0
        assert result.short_covering_sc == 0
        assert result.fresh_short_fs == 0
        assert result.long_unwinding_lu == 0
        assert result.bull_score == 0
        assert result.bear_score == 0
        assert result.net_lead == 0
    
    def test_accumulate_session_bull_lead(self):
        """Test session accumulation with BULL LEAD."""
        candles = [
            FuturesCandle(
                symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
                expiry="CUR", open_price=100, high_price=100,
                low_price=100, close_price=100, volume=1000, oi=5000
            ),
            FuturesCandle(
                symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
                expiry="CUR", open_price=100, high_price=102,
                low_price=100, close_price=101, volume=1200, oi=5500
            ),
        ]
        
        result = Gate8Calculator.accumulate_session(candles)
        
        assert result.fresh_long_fl == 500  # OI change from 5000 to 5500
        assert result.bull_score == 500
        assert result.lead_label == "BULL LEAD"
        assert result.ce_alignment is True
    
    def test_accumulate_session_bear_lead(self):
        """Test session accumulation with BEAR LEAD."""
        candles = [
            FuturesCandle(
                symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
                expiry="CUR", open_price=100, high_price=100,
                low_price=100, close_price=100, volume=1000, oi=5000
            ),
            FuturesCandle(
                symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
                expiry="CUR", open_price=100, high_price=100,
                low_price=98, close_price=99, volume=1200, oi=5500
            ),
        ]
        
        result = Gate8Calculator.accumulate_session(candles)
        
        assert result.fresh_short_fs == 500
        assert result.bear_score == 500
        assert result.lead_label == "BEAR LEAD"
        assert result.pe_alignment is True
    
    def test_accumulate_session_idempotent(self):
        """Test AT-07: Same candle processed only once."""
        candles = [
            FuturesCandle(
                symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
                expiry="CUR", open_price=100, high_price=100,
                low_price=100, close_price=100, volume=1000, oi=5000
            ),
            FuturesCandle(
                symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
                expiry="CUR", open_price=100, high_price=102,
                low_price=100, close_price=101, volume=1200, oi=5500
            ),
        ]
        
        result1 = Gate8Calculator.accumulate_session(candles)
        result2 = Gate8Calculator.accumulate_session(candles)
        
        assert result1.bull_score == result2.bull_score
        assert result1.net_lead == result2.net_lead


class TestGatesCalculator:
    """Test multi-gate evaluation and readiness."""
    
    def test_evaluate_readiness_8_passes(self):
        """Test readiness: 8 passes = Full-quantity."""
        gate_results = {i: ("PASS", f"Gate {i} passed") for i in range(1, 9)}
        status, desc = GatesCalculator.evaluate_readiness(gate_results)
        
        assert status == "Full-quantity readiness"
    
    def test_evaluate_readiness_6_passes(self):
        """Test readiness: 6-7 passes = Half-quantity."""
        gate_results = {i: ("PASS" if i <= 6 else "FAIL", f"Gate {i}") for i in range(1, 9)}
        status, desc = GatesCalculator.evaluate_readiness(gate_results)
        
        assert status == "Half-quantity readiness"
    
    def test_evaluate_readiness_4_passes(self):
        """Test readiness: 4-5 passes = Wait."""
        gate_results = {i: ("PASS" if i <= 4 else "FAIL", f"Gate {i}") for i in range(1, 9)}
        status, desc = GatesCalculator.evaluate_readiness(gate_results)
        
        assert status == "Wait — one more gate needed"
    
    def test_evaluate_readiness_below_4(self):
        """Test readiness: Below 4 passes = Stay out."""
        gate_results = {i: ("PASS" if i <= 3 else "FAIL", f"Gate {i}") for i in range(1, 9)}
        status, desc = GatesCalculator.evaluate_readiness(gate_results)
        
        assert status == "Stay out"
    
    def test_evaluate_readiness_opposite_signal(self):
        """Test readiness: Opposite signal = Exit/Stay out."""
        gate_results = {i: ("PASS" if i <= 6 else "OPPOSITE", f"Gate {i}") for i in range(1, 9)}
        status, desc = GatesCalculator.evaluate_readiness(gate_results)
        
        assert "Exit" in status or "Stay out" in status


class TestAcceptanceTests:
    """Acceptance tests from requirements document."""
    
    def test_at_01_fresh_long_build(self):
        """AT-01: Close rises and OI rises = Fresh Long Build; CE bias."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100, low_price=100,
            close_price=100, volume=1000, oi=5000
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=102, low_price=100,
            close_price=101, volume=1200, oi=5500
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.direction_label == "Fresh Long Build"
        assert result.bias == "Bullish / CE"
    
    def test_at_02_short_covering(self):
        """AT-02: Close rises and OI falls = Short Covering; CE bias."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100, low_price=100,
            close_price=100, volume=1000, oi=5000
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=102, low_price=100,
            close_price=101, volume=1200, oi=4500
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.direction_label == "Short Covering"
        assert result.bias == "Bullish / CE"
    
    def test_at_03_fresh_short_build(self):
        """AT-03: Close falls and OI rises = Fresh Short Build; PE bias."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100, low_price=100,
            close_price=100, volume=1000, oi=5000
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=100, low_price=98,
            close_price=99, volume=1200, oi=5500
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.direction_label == "Fresh Short Build"
        assert result.bias == "Bearish / PE"
    
    def test_at_04_long_unwinding(self):
        """AT-04: Close falls and OI falls = Long Unwinding; PE bias."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100, low_price=100,
            close_price=100, volume=1000, oi=5000
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=100, low_price=98,
            close_price=99, volume=1200, oi=4500
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.direction_label == "Long Unwinding"
        assert result.bias == "Bearish / PE"
    
    def test_at_05_neutral_unclassified(self):
        """AT-05: Price flat or OI missing = Neutral/unclassified or data missing."""
        previous = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
            expiry="CUR", open_price=100, high_price=100, low_price=100,
            close_price=100, volume=1000, oi=0
        )
        
        current = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR", open_price=100, high_price=100, low_price=100,
            close_price=100, volume=1200, oi=0
        )
        
        result = Gate7Calculator.calculate(current, previous, 1000, 300, 50)
        
        assert result.price_direction == "FLAT"
        assert "Neutral" in result.direction_label
        assert result.bias == "Neutral"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
