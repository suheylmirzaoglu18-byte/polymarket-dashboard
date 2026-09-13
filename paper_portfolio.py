import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class Position:
    token_id: str
    title: str
    side: str
    size: float
    avg_price: float
    cost_usd: float
    opened_at: str
    target_wallet: str
    last_update: str = ""
    mark_price: float = 0.0

@dataclass
class TradeRecord:
    ts: str
    target: str
    action: str
    token_id: str
    title: str
    size_usd: float
    price: float
    shares: float
    mode: str
    status: str

class PaperPortfolio:
    def __init__(self, starting_cash: float = 1000.0, state_file: str = "state/paper_state.json"):
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeRecord] = []
        self.realized_pnl = 0.0
        self.state_file = state_file
        self._ensure_dirs()
        self.load()
        # Add sample data if empty (for first run on cloud)
        if len(self.positions) == 0:
            self._add_sample_data()

    def _ensure_dirs(self):
        try:
            os.makedirs(os.path.dirname(self.state_file) or ".", exist_ok=True)
            os.makedirs("logs", exist_ok=True)
        except:
            pass

    def _add_sample_data(self):
        self.open_position("btc15m", "Bitcoin Up or Down - 15 Minutes", "YES", 12.0, 0.48, "0xSportsWhale")
        self.open_position("nba1", "Lakers vs Celtics - Lakers win", "YES", 8.5, 0.62, "0xNBASpecialist")
        self.open_position("btc5m", "BTC Up or Down - 5 Minutes", "NO", 20.0, 0.41, "0xBTCScalper")

    def load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                self.cash = float(data.get("cash", self.starting_cash))
                self.realized_pnl = float(data.get("realized_pnl", 0.0))
                self.starting_cash = float(data.get("starting_cash", self.starting_cash))
                for tid, p in data.get("positions", {}).items():
                    p.pop("mark_price", None)
                    self.positions[tid] = Position(**p)
            except:
                pass

    def save(self):
        try:
            data = {
                "starting_cash": self.starting_cash,
                "cash": round(self.cash, 4),
                "realized_pnl": round(self.realized_pnl, 4),
                "positions": {tid: asdict(p) for tid, p in self.positions.items()},
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def open_position(self, token_id, title, side, usd_size, price, target_wallet):
        if price <= 0 or price >= 1:
            return False
        shares = usd_size / price
        self.cash -= usd_size
        now = datetime.now(timezone.utc).isoformat()
        self.positions[token_id] = Position(
            token_id=token_id, title=title[:120], side=side,
            size=shares, avg_price=price, cost_usd=usd_size,
            opened_at=now, target_wallet=target_wallet[:14], last_update=now
        )
        self.trade_history.append(TradeRecord(
            ts=now, target=target_wallet[:14], action="BUY",
            token_id=token_id, title=title[:90], size_usd=usd_size,
            price=price, shares=shares, mode="PAPER", status="FILLED"
        ))
        self.save()
        return True

    def position_value(self):
        return sum(p.size * (p.mark_price if p.mark_price > 0 else p.avg_price) for p in self.positions.values())

    def unrealized_pnl(self):
        return sum((p.size * (p.mark_price if p.mark_price > 0 else p.avg_price)) - p.cost_usd for p in self.positions.values())

    def equity(self):
        return self.cash + self.position_value()

    def total_pnl(self):
        return self.realized_pnl + self.unrealized_pnl()

    def return_pct(self):
        if self.starting_cash
