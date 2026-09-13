import json
import os
from datetime import datetime, timezone
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
    def __init__(self, starting_cash=1000.0, state_file="state/paper_state.json"):
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.positions = {}
        self.trade_history = []
        self.realized_pnl = 0.0
        self.state_file = state_file
        self.load()
        if len(self.positions) == 0:
            self._add_sample()

    def _add_sample(self):
        self.open_position("btc15m", "Bitcoin Up or Down - 15 Minutes", "YES", 12.0, 0.48, "0xSportsWhale")
        self.open_position("nba1", "Lakers vs Celtics - Lakers win", "YES", 8.5, 0.62, "0xNBASpecialist")
        self.open_position("btc5m", "BTC Up or Down - 5 Minutes", "NO", 20.0, 0.41, "0xBTCScalper")

    def load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                self.cash = float(data.get("cash", self.starting_cash))
                self.realized_pnl = float(data.get("realized_pnl", 0))
                for tid, p in data.get("positions", {}).items():
                    p.pop("mark_price", None)
                    self.positions[tid] = Position(**p)
            except:
                pass

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.state_file) or ".", exist_ok=True)
            data = {
                "starting_cash": self.starting_cash,
                "cash": round(self.cash, 4),
                "realized_pnl": round(self.realized_pnl, 4),
                "positions": {k: asdict(v) for k, v in self.positions.items()},
            }
            with open(self.state_file, "w") as f:
                json.dump(data, f)
        except:
            pass

    def open_position(self, token_id, title, side, usd_size, price, target_wallet):
        shares = usd_size / price
        self.cash -= usd_size
        now = datetime.now(timezone.utc).isoformat()
        self.positions[token_id] = Position(
            token_id, title[:100], side, shares, price, usd_size, now, target_wallet[:12], now
        )
        self.trade_history.append(TradeRecord(
            now, target_wallet[:12], "BUY", token_id, title[:80],
            usd_size, price, shares, "PAPER", "FILLED"
        ))
        self.save()
        return True

    def position_value(self):
        return sum(p.size * (p.mark_price or p.avg_price) for p in self.positions.values())

    def unrealized_pnl(self):
        return sum(p.size * (p.mark_price or p.avg_price) - p.cost_usd for p in self.positions.values())

    def equity(self):
        return self.cash + self.position_value()

    def summary_dict(self):
        return {
            "starting_cash": self.starting_cash,
            "cash": round(self.cash, 2),
            "position_value": round(self.position_value(), 2),
            "equity": round(self.equity(), 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "unrealized_pnl": round(self.unrealized_pnl(), 2),
            "total_pnl": round(self.realized_pnl + self.unrealized_pnl(), 2),
            "return_pct": round((self.equity() - self.starting_cash) / self.starting_cash * 100, 2),
            "open_positions": len(self.positions),
            "total_trades": len(self.trade_history),
        }

    def positions_list(self):
        rows = []
        for p in self.positions.values():
            px = p.mark_price or p.avg_price
            rows.append({
                "Title": p.title[:60],
                "Side": p.side,
                "Shares": round(p.size, 1),
                "Avg Price": round(p.avg_price, 3),
                "Cost $": round(p.cost_usd, 2),
                "Value $": round(p.size * px, 2),
                "Unrealized $": round(p.size * px - p.cost_usd, 2),
                "Target": p.target_wallet,
            })
        return rows

    def trades_list(self, limit=30):
        rows = []
        for t in reversed(self.trade_history[-limit:]):
            rows.append({
                "Time": t.ts[:16].replace("T", " "),
                "Action": t.action,
                "Title": t.title[:50],
                "Size $": round(t.size_usd, 2),
                "Price": round(t.price, 3),
                "Target": t.target,
            })
        return rows
