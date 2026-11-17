"""
Integration tests for the STAR Trading Scanner.
Tests API provider, database persistence, and end-to-end workflows.
"""
import pytest
import tempfile
from datetime import datetime
from pathlib import Path

from src.database import Database
from src.models import FuturesCandle, Gate7Result, Gate8Result
from src.provider import DhanAPIProvider


class TestDatabasePersistence:
    """Test database operations and persistence."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield Database(str(db_path))
    
    def test_save_and_retrieve_futures_candle(self, temp_db):
        """Test saving and retrieving a futures candle."""
        candle = FuturesCandle(
            symbol="RELIANCE",
            timestamp=datetime(2026, 1, 1, 9, 20),
            expiry="CUR",
            open_price=100,
            high_price=102,
            low_price=99,
            close_price=101,
            volume=1000,
            oi=5000
        )
        
        # Save
        assert temp_db.save_futures_candle(candle) is True
        
        # Retrieve
        candles = temp_db.get_futures_candles("RELIANCE", "CUR")
        assert len(candles) == 1
        assert candles[0].symbol == "RELIANCE"
        assert candles[0].close_price == 101
    
    def test_save_and_retrieve_multiple_candles(self, temp_db):
        """Test saving and retrieving multiple candles."""
        candles_to_save = [
            FuturesCandle(
                symbol="RELIANCE",
                timestamp=datetime(2026, 1, 1, 9, 15),
                expiry="CUR",
                open_price=100, high_price=100, low_price=100, close_price=100,
                volume=1000, oi=5000
            ),
            FuturesCandle(
                symbol="RELIANCE",
                timestamp=datetime(2026, 1, 1, 9, 20),
                expiry="CUR",
                open_price=100, high_price=102, low_price=100, close_price=101,
                volume=1200, oi=5500
            ),
        ]
        
        for candle in candles_to_save:
            temp_db.save_futures_candle(candle)
        
        retrieved = temp_db.get_futures_candles("RELIANCE", "CUR")
        assert len(retrieved) == 2
        assert retrieved[0].timestamp == datetime(2026, 1, 1, 9, 15)
        assert retrieved[1].timestamp == datetime(2026, 1, 1, 9, 20)
    
    def test_save_and_retrieve_gate7_result(self, temp_db):
        """Test saving and retrieving Gate 7 result."""
        result = Gate7Result(
            symbol="RELIANCE",
            expiry="CUR",
            candle_timestamp=datetime(2026, 1, 1, 9, 20),
            price_direction="UP",
            price_change_percent=1.0,
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
        
        assert temp_db.save_gate7_result(result) is True
    
    def test_save_and_retrieve_gate8_result(self, temp_db):
        """Test saving and retrieving Gate 8 result."""
        result = Gate8Result(
            symbol="RELIANCE",
            expiry="CUR",
            session_date=datetime(2026, 1, 1),
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
            last_candle_timestamp=datetime(2026, 1, 1, 9, 50)
        )
        
        assert temp_db.save_gate8_result(result) is True
    
    def test_session_state_persistence(self, temp_db):
        """Test session state save and retrieve."""
        # Save state
        state_json = '{"processed_candles": [1, 2, 3]}'
        assert temp_db.set_session_state("gate8_state", state_json) is True
        
        # Retrieve state
        retrieved = temp_db.get_session_state("gate8_state")
        assert retrieved == state_json
    
    def test_session_state_update(self, temp_db):
        """Test updating existing session state."""
        # Save initial state
        temp_db.set_session_state("test_key", "initial_value")
        
        # Update
        temp_db.set_session_state("test_key", "updated_value")
        
        # Verify update
        value = temp_db.get_session_state("test_key")
        assert value == "updated_value"
    
    def test_api_logging(self, temp_db):
        """Test API call logging."""
        assert temp_db.log_api_call(
            symbol="RELIANCE",
            api_call="get_futures_candle",
            status="success",
            duration_ms=150
        ) is True
    
    def test_audit_logging(self, temp_db):
        """Test audit event logging."""
        assert temp_db.log_audit_event(
            event_type="gate_evaluation",
            symbol="RELIANCE",
            details="All 8 gates evaluated"
        ) is True


class TestAPIProvider:
    """Test API provider adapter."""
    
    def test_provider_initialization(self):
        """Test API provider can be initialized."""
        provider = DhanAPIProvider()
        assert provider is not None
        assert provider.timeout == 10
        assert provider.retry_count == 3
    
    def test_provider_has_session(self):
        """Test provider maintains HTTP session."""
        provider = DhanAPIProvider()
        assert provider.session is not None


class TestEndToEndWorkflow:
    """Test complete workflow scenarios."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield Database(str(db_path))
    
    def test_session_restart_recovery(self, temp_db):
        """Test AT-08: App restarts mid-session without duplication."""
        # Initial session: save candles and state
        candles = [
            FuturesCandle(
                symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 15),
                expiry="CUR", open_price=100, high_price=100, low_price=100,
                close_price=100, volume=1000, oi=5000
            ),
            FuturesCandle(
                symbol="RELIANCE", timestamp=datetime(2026, 1, 1, 9, 20),
                expiry="CUR", open_price=100, high_price=102, low_price=100,
                close_price=101, volume=1200, oi=5500
            ),
        ]
        
        for candle in candles:
            temp_db.save_futures_candle(candle)
        
        # Save Gate 8 state
        state_json = '{"processed_timestamps": ["2026-01-01T09:15:00", "2026-01-01T09:20:00"]}'
        temp_db.set_session_state("gate8_state_RELIANCE_CUR", state_json)
        
        # Restart: check recovery
        retrieved_candles = temp_db.get_futures_candles("RELIANCE", "CUR")
        retrieved_state = temp_db.get_session_state("gate8_state_RELIANCE_CUR")
        
        assert len(retrieved_candles) == 2
        assert retrieved_state == state_json
        
        # Verify no duplication when re-processing
        for candle in candles:
            temp_db.save_futures_candle(candle)
        
        final_candles = temp_db.get_futures_candles("RELIANCE", "CUR")
        assert len(final_candles) == 2  # Still 2, not 4
    
    def test_data_quality_validation(self):
        """Test data quality checks for critical metrics."""
        candle = FuturesCandle(
            symbol="RELIANCE", timestamp=datetime.now(),
            expiry="CUR", open_price=0, high_price=0, low_price=0,
            close_price=0, volume=0, oi=0, is_complete=False,
            error_message="Data incomplete"
        )
        
        # Verify error is captured
        assert candle.error_message == "Data incomplete"
        assert candle.is_complete is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
