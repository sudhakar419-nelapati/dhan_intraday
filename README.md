# STAR Trading Scanner

## Overview

STAR Trading Scanner is a decision-support tool for NSE F&O stocks built on the STAR 8-Gate Trade Checklist. It evaluates option chains and 5-minute futures candles to provide transparent readiness indicators for call spread (CE) and put spread (PE) positions.

**IMPORTANT**: This is a decision-support scanner, NOT an automated order execution system. It does not place trades.

## Features

### Core Functionality
- **8-Gate Evaluation**: Implements all STAR gates (1-8) for independent CE and PE analysis
- **Gate 7 (Futures Read)**: Analyzes latest 5-minute futures candle with price/OI classification
- **Gate 8 (Futures Neutralization)**: Accumulates session-wide bullish/bearish activity from 09:15 IST
- **Options Analysis**: Gates 1-6 evaluate options chain data (OI Wall, GEX, Seller activity, etc.)
- **Transparent Results**: Shows evidence for each gate pass/fail/weak/opposite determination
- **Session Persistence**: Recovers from restarts without duplicating aggregations

### Dashboard
- **Market Scanner**: Column-based view of all NSE F&O stocks with readiness status
- **Stock Detail**: Historical 5-minute candles, charts, full gate checklist, session accumulation
- **Logs & Diagnostics**: API call history, audit trail, system health
- **Settings**: Configurable thresholds, baselines, feature flags

### Data Quality
- Explicit "MISSING" / "STALE" indicators instead of silent zeros
- Coverage percentage for options chain
- Source timestamps and API error tracking
- Candle completeness validation

## Project Structure

```
dhan_intraday/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── models.py          # Data models (FuturesCandle, Gate7Result, etc.)
│   ├── provider.py        # Dhan API adapter
│   ├── gates.py           # Gate 1-8 calculation engine
│   ├── database.py        # SQLite persistence layer
│   └── baselines.py       # Historical baseline calculations
├── tests/
│   ├── __init__.py
│   ├── test_gates.py      # Unit tests for gate logic
│   ├── test_integration.py # Integration tests (DB, API, workflows)
│   └── test_models.py     # Model and configuration tests
├── data/                  # SQLite database directory
├── logs/                  # Application logs
├── dashboard.py           # Streamlit web interface
├── requirements.txt       # Python dependencies
├── .env.example           # Configuration template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Setup & Configuration

### Prerequisites
- Python 3.8+
- Dhan API credentials (API key and Client ID)
- pip package manager

### Installation

1. **Clone or navigate to project**:
   ```bash
   cd C:\Users\ADMIN\IdeaProjects\dhan_intraday
   ```

2. **Create and activate virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   - `DHAN_API_KEY`: Your Dhan API key
   - `DHAN_CLIENT_ID`: Your Dhan Client ID
   - `UNIVERSE_SYMBOLS`: Comma-separated list of symbols to scan
   - Other thresholds as needed

### Validation

```bash
python -c "from src.config import validate_config; validate_config()"
```

## Running the Scanner

### Start the Dashboard
```bash
streamlit run dashboard.py
```

This opens the web interface at `http://localhost:8501`

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_gates.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Command-Line Usage (Future)
```bash
python -m scanner.cli --symbol RELIANCE --scan --detail --export
```

## Gate Evaluation Details

### Gate 1: OI Wall
- Identifies strike concentration in OI
- Displays CE/PE dominance and wall stability
- Signals: PASS / FAIL / WEAK / DATA_MISSING

### Gate 2: Strike GEX
- Calculates net gamma exposure
- Requires ≥80% options coverage
- Tracks 1-minute GEX change

### Gate 3: Seller Neutralization
- Evaluates seller OI balance across sides
- Preserves existing classification method

### Gate 4: CE/PE Seller Exit
- Checks OI exit (reduction) with volume confirmation
- Thresholds: wall cut >1.00%, OI strength >1.40x, volume strength >1.40x

### Gate 5: CE/PE Writing
- Detects new seller (writing) activity
- Displays: BLANK / LOW / ACTIVE

### Gate 6: CE/PE Buying
- Detects buyer activity and strength
- Displays: BLANK / WEAK / ACTIVE

### Gate 7: Futures Read
- **Question**: What are futures traders doing in this exact 5-minute period?
- **Metrics**:
  - Price direction (UP / DOWN / FLAT)
  - OI direction (UP / DOWN / FLAT)
  - Strength indicators (OI strength, volume strength, volume rank)
- **Classification**:
  - UP + UP = "Fresh Long Build" → Bullish/CE bias
  - UP + DOWN = "Short Covering" → Bullish/CE bias
  - DOWN + UP = "Fresh Short Build" → Bearish/PE bias
  - DOWN + DOWN = "Long Unwinding" → Bearish/PE bias

**Quality Rules**:
- OI strength < 1.0x = weak/unreliable
- OI strength 1.0x–1.4x = medium confidence
- OI strength > 1.4x = strong confirmation
- Volume rank #250+ = low confidence
- Volume rank > #300 = mark unreliable

### Gate 8: Futures Neutralization
- **Question**: Who has been winning the entire session from 09:15 IST to now?
- **Buckets** (accumulate session-wide):
  - FL (Fresh Long): Price UP + OI UP
  - SC (Short Covering): Price UP + OI DOWN
  - FS (Fresh Short): Price DOWN + OI UP
  - LU (Long Unwinding): Price DOWN + OI DOWN
- **Scores**:
  - Bull Score = FL + SC
  - Bear Score = FS + LU
  - Net Lead = Bull Score − Bear Score
- **Alignment**:
  - Positive net lead → BULL LEAD (aligns with CE)
  - Negative net lead → BEAR LEAD (aligns with PE)
  - Within neutral band → NEUTRAL

## Readiness Determination

Based on playbook decision bands:

| Pass Count | Status | Interpretation |
|-----------|--------|-----------------|
| 8 | Full-quantity | Strongest readiness |
| 6-7 | Half-quantity | Good readiness |
| 4-5 | Wait | Need one more gate |
| Below 4 | Stay out | Insufficient |

**Special**: Any strong OPPOSITE signal → Exit if already in / Stay out if not

## Data Model

### FuturesCandle
```python
{
  symbol: str,              # e.g., "RELIANCE"
  timestamp: datetime,      # IST time of candle close
  expiry: str,             # e.g., "CUR"
  open/high/low/close: float,
  volume: float,
  oi: float,
  source_timestamp: datetime,
  is_complete: bool,       # Candle is fully formed
  error_message: Optional[str]
}
```

### Gate7Result
Includes price direction, OI direction, strength metrics, classification label, bias, reliability flag.

### Gate8Result
Includes FL/SC/FS/LU buckets, bull/bear scores, net lead, alignment status.

### GateChecklistResult
Complete evaluation of all 8 gates with pass/fail/weak/opposite status and reasons for each.

## Database Schema

**SQLite persistent storage** for:
- `futures_candles` - Raw 5-minute futures data
- `gate7_results` - Computed Gate 7 metrics per candle
- `gate8_results` - Accumulated Gate 8 session totals
- `gate_checklists` - Full 8-gate evaluations
- `session_state` - Recovery state (processed timestamps, etc.)
- `api_logs` - API call history and performance
- `audit_logs` - Event audit trail

## Configuration Reference

### Thresholds
- `PRICE_NOISE_THRESHOLD`: Minimum price movement to register as UP/DOWN (default: 0.0001)
- `OI_STRENGTH_WEAK`: Minimum multiplier for reliable signal (default: 1.0x)
- `OI_STRENGTH_MEDIUM_LOW`: Medium-strength threshold (default: 1.4x)
- `VOLUME_RANK_STRONG`: Top N candles in session (default: 100)
- `VOLUME_RANK_MODERATE`: Moderate rank cutoff (default: 250)
- `VOLUME_RANK_WARNING`: Below this = low confidence (default: 300)

### Baseline & Session
- `BASELINE_LOOKBACK_SESSIONS`: Sessions to average over (default: 5)
- `NEUTRAL_BAND`: Minimum movement to avoid trivial trades (default: 0.0)
- `SESSION_START_TIME`: IST market open (default: 09:15)
- `SESSION_END_TIME`: IST market close (default: 15:30)

### API & Performance
- `API_TIMEOUT_SECONDS`: Request timeout (default: 10)
- `API_RETRY_COUNT`: Retry attempts on failure (default: 3)
- `API_RETRY_DELAY_SECONDS`: Delay between retries (default: 2)
- `MAX_CONCURRENT_SYMBOLS`: Parallel processing limit (default: 5)
- `MIN_OPTIONS_COVERAGE_PERCENT`: Required strike coverage (default: 80%)

### Logging
- `LOG_LEVEL`: Verbosity (INFO, DEBUG, ERROR) (default: INFO)
- `LOG_PATH`: Output directory (default: ./logs)

### Feature Flags
- `PAPER_MODE`: Use simulated data (default: false)
- `ENABLE_HISTORICAL_REPLAY`: Load historical sessions (default: false)

## Testing

### Test Coverage

**Unit Tests** (`tests/test_gates.py`):
- Direction classification (all 4 directions + flat)
- Strength calculations (weak/medium/strong)
- Reliability checks
- Gate 7 & 8 calculations
- All acceptance tests (AT-01 through AT-14)

**Integration Tests** (`tests/test_integration.py`):
- Database persistence and recovery
- API provider initialization
- End-to-end workflows
- Session restart without duplication

**Model Tests** (`tests/test_models.py`):
- Data model creation
- Configuration validation

### Running Tests

```bash
# Full test suite
pytest tests/ -v --tb=short

# Run only acceptance tests
pytest tests/test_gates.py::TestAcceptanceTests -v

# Generate coverage report
pytest tests/ --cov=src --cov-report=html
```

## Acceptance Criteria

| ID | Test | Expected Result |
|----|------|-----------------|
| AT-01 | Close ↑, OI ↑ | Fresh Long Build; CE bias |
| AT-02 | Close ↑, OI ↓ | Short Covering; CE bias |
| AT-03 | Close ↓, OI ↑ | Fresh Short Build; PE bias |
| AT-04 | Close ↓, OI ↓ | Long Unwinding; PE bias |
| AT-05 | Price flat or OI missing | Neutral/unclassified or DATA_MISSING |
| AT-06 | Insufficient baseline history | Show "INSUFFICIENT BASELINE" |
| AT-07 | Same candle processed twice | Gate 8 updates once only (idempotent) |
| AT-08 | App restarts mid-session | Session totals recover without duplication |
| AT-09 | Gate 4: 1.2% cut, 1.5x OI, 1.6x vol | Gate 4 passes |
| AT-10 | Any Gate 4 threshold fails | Gate 4 fails with reason |
| AT-11 | Options coverage <80% | Gate 2 shows incomplete coverage |
| AT-12 | One symbol API fails | Other symbols continue; failed symbol shows error |
| AT-13 | Holiday/non-trading day | No false active-session signal |
| AT-14 | Futures expiry rolls | No cross-contract OI comparison |

## Known Limitations & Owner Decisions Pending

1. **Gate 8 Totals Mismatch** (Playbook inconsistency)
   - Confirm whether 10.2L/7.4L are gross totals or another measure
   - Formula implemented: FL+SC and FS+LU as stated

2. **OI Strength Baseline**
   - Implemented: Same 5-minute clock slot over previous 5 sessions
   - Confirm alternative (rolling 20 candles, etc.)

3. **Volume % Baseline**
   - Implemented: Same 5-minute slot over previous 5 sessions
   - Confirm alternative baseline definition

4. **Candle OI Semantics**
   - Confirm whether Dhan OI is end-of-candle snapshot

5. **FL/SC/FS/LU Accumulation**
   - Confirm absolute OI delta, signed delta, or weighted values

6. **GEX Formula**
   - Needs owner-provided formula with gamma, multiplier, spot/futures inputs

7. **Seller/Buyer Inference**
   - Reuses existing classification method (not raw OI/volume alone)
   - Provide existing formula/code if available

8. **Wall Cut Denominator**
   - Confirm opening OI, previous-candle OI, or rolling reference

9. **Neutral Bands & Opposite Signal Override**
   - Confirm minimum price/OI movement thresholds
   - Confirm whether opposite signal overrides numeric pass count exactly as written

## Security

- **No hardcoded credentials**: All secrets in environment variables
- **Masked logging**: API keys and sensitive data masked in logs
- **No automatic trading**: Decision-support only; manual trade placement required
- **Credential isolation**: `.env` file excluded from git

## Performance

- **Gate 7**: O(1) per candle; calculated once per newly completed 5-minute candle
- **Gate 8**: O(n) per session; processes each candle once; persisted state prevents re-computation
- **Concurrency**: Bounded by `MAX_CONCURRENT_SYMBOLS` to respect API limits
- **Caching**: Invalidated when universe, expiry, session date, or parameters change

## Troubleshooting

### API Connection Failed
```
Error: "DHAN_API_KEY not configured properly"
Solution: Check .env file; run validate_config()
```

### Insufficient Baseline
```
Message: "INSUFFICIENT BASELINE (5 sessions required)"
Solution: Wait for more historical sessions or reduce BASELINE_LOOKBACK_SESSIONS
```

### Database Locked
```
Error: "database is locked"
Solution: Ensure only one instance of dashboard/scanner is running
```

### High API Latency
```
Problem: Slow refresh or timeouts
Solution: Increase API_TIMEOUT_SECONDS or reduce MAX_CONCURRENT_SYMBOLS
```

## Contributing

1. Write tests for new features (see `tests/` for examples)
2. Run full test suite before committing
3. Update README for new parameters or gates
4. Mask sensitive data in logs
5. Follow existing code style (Python PEP 8)

## License

[Specify your license]

## Support

For issues, feature requests, or gate formula definitions, contact the STAR Trading team.

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-17  
**Status**: Ready for integration testing with live Dhan API data
