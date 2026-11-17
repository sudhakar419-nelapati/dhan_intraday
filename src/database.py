"""
Data persistence layer for STAR Trading Scanner.
Handles database operations and session state recovery.
"""
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from .models import (
    FuturesCandle, OptionChainSnapshot, Gate7Result, Gate8Result, GateChecklistResult
)
from .config import DB_PATH

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for persistent storage."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Initialize database tables if not exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Futures candles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS futures_candles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                expiry TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume REAL,
                oi REAL,
                source_timestamp DATETIME,
                is_complete BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, expiry, timestamp)
            )
        """)
        
        # Gate 7 results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gate7_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                expiry TEXT NOT NULL,
                candle_timestamp DATETIME NOT NULL,
                price_direction TEXT,
                price_change_percent REAL,
                oi_change REAL,
                oi_change_percent REAL,
                futures_volume REAL,
                futures_volume_percent REAL,
                oi_strength REAL,
                volume_strength REAL,
                volume_rank INTEGER,
                direction_label TEXT,
                bias TEXT,
                is_reliable BOOLEAN,
                signal_strength TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, expiry, candle_timestamp)
            )
        """)
        
        # Gate 8 results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gate8_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                expiry TEXT NOT NULL,
                session_date DATE NOT NULL,
                fresh_long_fl REAL,
                short_covering_sc REAL,
                fresh_short_fs REAL,
                long_unwinding_lu REAL,
                bull_score REAL,
                bear_score REAL,
                net_lead REAL,
                lead_label TEXT,
                ce_alignment BOOLEAN,
                pe_alignment BOOLEAN,
                candle_count INTEGER,
                last_candle_timestamp DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, expiry, session_date)
            )
        """)
        
        # Gate checklist results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gate_checklists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                expiry TEXT NOT NULL,
                side TEXT NOT NULL,
                gate_results TEXT,
                pass_count INTEGER,
                readiness_status TEXT,
                readiness_description TEXT,
                first_failed_gate INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, expiry, side, created_at)
            )
        """)
        
        # Session state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                api_call TEXT,
                status TEXT,
                duration_ms INTEGER,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Audit logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                symbol TEXT,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_futures_candle(self, candle: FuturesCandle) -> bool:
        """Save a futures candle to database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO futures_candles
                (symbol, expiry, timestamp, open_price, high_price, low_price, close_price,
                 volume, oi, source_timestamp, is_complete)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                candle.symbol, candle.expiry, candle.timestamp,
                candle.open_price, candle.high_price, candle.low_price, candle.close_price,
                candle.volume, candle.oi, candle.source_timestamp, candle.is_complete
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving futures candle: {str(e)}")
            return False
    
    def get_futures_candles(
        self, symbol: str, expiry: str, limit: Optional[int] = None
    ) -> List[FuturesCandle]:
        """Retrieve futures candles from database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM futures_candles
                WHERE symbol = ? AND expiry = ?
                ORDER BY timestamp DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (symbol, expiry))
            rows = cursor.fetchall()
            conn.close()
            
            candles = []
            for row in rows:
                candle = FuturesCandle(
                    symbol=row["symbol"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    expiry=row["expiry"],
                    open_price=row["open_price"],
                    high_price=row["high_price"],
                    low_price=row["low_price"],
                    close_price=row["close_price"],
                    volume=row["volume"],
                    oi=row["oi"],
                    source_timestamp=datetime.fromisoformat(row["source_timestamp"]),
                    is_complete=bool(row["is_complete"])
                )
                candles.append(candle)
            
            return list(reversed(candles))  # Return in chronological order
        
        except Exception as e:
            logger.error(f"Error retrieving futures candles: {str(e)}")
            return []
    
    def save_gate7_result(self, result: Gate7Result) -> bool:
        """Save Gate 7 result to database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO gate7_results
                (symbol, expiry, candle_timestamp, price_direction, price_change_percent,
                 oi_change, oi_change_percent, futures_volume, futures_volume_percent,
                 oi_strength, volume_strength, volume_rank, direction_label, bias,
                 is_reliable, signal_strength)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.symbol, result.expiry, result.candle_timestamp,
                result.price_direction, result.price_change_percent,
                result.oi_change, result.oi_change_percent,
                result.futures_volume, result.futures_volume_percent,
                result.oi_strength, result.volume_strength, result.volume_rank,
                result.direction_label, result.bias, result.is_reliable, result.signal_strength
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving Gate 7 result: {str(e)}")
            return False
    
    def save_gate8_result(self, result: Gate8Result) -> bool:
        """Save Gate 8 result to database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO gate8_results
                (symbol, expiry, session_date, fresh_long_fl, short_covering_sc,
                 fresh_short_fs, long_unwinding_lu, bull_score, bear_score, net_lead,
                 lead_label, ce_alignment, pe_alignment, candle_count, last_candle_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.symbol, result.expiry, result.session_date,
                result.fresh_long_fl, result.short_covering_sc,
                result.fresh_short_fs, result.long_unwinding_lu,
                result.bull_score, result.bear_score, result.net_lead,
                result.lead_label, result.ce_alignment, result.pe_alignment,
                result.candle_count, result.last_candle_timestamp
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving Gate 8 result: {str(e)}")
            return False
    
    def save_gate_checklist(self, result: GateChecklistResult) -> bool:
        """Save gate checklist result to database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            gate_results_json = json.dumps({
                str(k): {"status": v[0], "reason": v[1]}
                for k, v in result.gate_results.items()
            })
            
            cursor.execute("""
                INSERT INTO gate_checklists
                (symbol, expiry, side, gate_results, pass_count, readiness_status,
                 readiness_description, first_failed_gate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.symbol, result.expiry, result.side, gate_results_json,
                result.pass_count, result.readiness_status, result.readiness_description,
                result.first_failed_gate
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving gate checklist: {str(e)}")
            return False
    
    def get_session_state(self, key: str) -> Optional[str]:
        """Retrieve session state value."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM session_state WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row["value"] if row else None
        except Exception as e:
            logger.error(f"Error retrieving session state: {str(e)}")
            return None
    
    def set_session_state(self, key: str, value: str) -> bool:
        """Save session state value."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO session_state (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving session state: {str(e)}")
            return False
    
    def log_api_call(
        self, symbol: str, api_call: str, status: str,
        duration_ms: int, error_message: Optional[str] = None
    ) -> bool:
        """Log API call details."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_logs (symbol, api_call, status, duration_ms, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol, api_call, status, duration_ms, error_message))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging API call: {str(e)}")
            return False
    
    def log_audit_event(
        self, event_type: str, symbol: Optional[str] = None, details: Optional[str] = None
    ) -> bool:
        """Log audit event."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (event_type, symbol, details)
                VALUES (?, ?, ?)
            """, (event_type, symbol, details))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            return False
