# Configuration for Polymarket Copy Trading Dashboard

TARGETS = [
    # Add real wallet addresses here later
]

COPY_RATIO = 0.10
MAX_TRADE_USD = 40.0
MIN_TRADE_USD = 3.0
MAX_OPEN_POSITIONS = 15
DAILY_LOSS_LIMIT_USD = 150.0

ALLOWED_KEYWORDS = [
    "btc", "bitcoin", "eth", "ethereum", "sol", "solana",
    "up or down", "up/down", "15m", "5m", "1h",
    "nba", "nfl", "mlb", "nhl", "soccer", "football",
    "premier league", "uefa", "champions league", "la liga",
    "serie a", "bundesliga", "ligue 1", "tennis", "ufc", "mma",
    "world cup", "euro", "copa"
]

PAPER_TRADING = True
POLL_INTERVAL_SEC = 4

STATE_FILE = "state/paper_state.json"
