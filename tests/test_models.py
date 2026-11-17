"""
Tests for data models and configuration.
"""
import pytest
from datetime import datetime
from src.models import FuturesCandle, Gate7Result, Gate8Result, GateChecklistResult
from src.config import validate_config


class TestModelsCreation:
    """Test that models can be created correctly."""
    
    def test_futures_candle_creation(self):
        """Test FuturesCandle model creation."""
        candle = FuturesCandle(
            symbol="RELIANCE",
            timestamp=datetime.now(),
            expiry="CUR",
            open_price=100,
            high_price=102,
            low_price=99,
            close_price=101,
            volume=1000,
            oi=5000
        )
        
        assert candle.symbol == "RELIANCE"
        assert candle.close_price == 101
        assert candle.volume == 1000
        assert candle.oi == 5000
    
    def test_gate7_result_creation(self):
        """Test Gate7Result model creation."""
        result = Gate7Result(
            symbol="RELIANCE",
            expiry="CUR",
            candle_timestamp=datetime.now(),
            price_direction="UP",
            price_change_percent=1.5,
            oi_change=500,
            oi_change_percent=10.0,
            futures_volume=1200,
            futures_volume_percent=20.0,
            oi_strength=1.5,
            volume_strength=1.2,
            volume_rank=50,
            direction_label="Fresh Long Build",
            bias="Bullish / CE",
            is_reliable=True,
            signal_strength="strong"
        )
        
        assert result.symbol == "RELIANCE"
        assert result.direction_label == "Fresh Long Build"
        assert result.is_reliable is True
    
    def test_gate8_result_creation(self):
        """Test Gate8Result model creation."""
        result = Gate8Result(
            symbol="RELIANCE",
            expiry="CUR",
            session_date=datetime.now(),
            fresh_long_fl=2.1,
            short_covering_sc=3.5,
            fresh_short_fs=1.9,
            long_unwinding_lu=3.8,
            bull_score=5.6,
            bear_score=5.7,
            net_lead=-0.1,
            lead_label="NEUTRAL",
            ce_alignment=False,
            pe_alignment=False,
            candle_count=10,
            last_candle_timestamp=datetime.now()
        )
        
        assert result.symbol == "RELIANCE"
        assert result.bull_score == 5.6
        assert result.bear_score == 5.7
        assert result.lead_label == "NEUTRAL"
    
    def test_gate_checklist_result_creation(self):
        """Test GateChecklistResult model creation."""
        gate_results = {
            1: ("PASS", "OI Wall detected"),
            2: ("PASS", "GEX calculation confirmed"),
            3: ("FAIL", "Insufficient seller lead"),
            4: ("PASS", "Seller exit confirmed"),
            5: ("FAIL", "No writing activity"),
            6: ("PASS", "Buying activity detected"),
            7: ("PASS", "Bullish bias: Fresh Long Build"),
            8: ("FAIL", "No bear alignment"),
        }
        
        result = GateChecklistResult(
            symbol="RELIANCE",
            expiry="CUR",
            side="CE",
            gate_results=gate_results,
            pass_count=5,
            readiness_status="Wait — one more gate needed",
            readiness_description="5 gates passed (4-5)",
            first_failed_gate=3
        )
        
        assert result.symbol == "RELIANCE"
        assert result.side == "CE"
        assert result.pass_count == 5
        assert result.first_failed_gate == 3


class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_config_validation(self):
        """Test configuration can be validated."""
        # This should warn but not fail completely in test environment
        is_valid = validate_config()
        # We expect it to be False since API keys are not configured in tests
        assert isinstance(is_valid, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
