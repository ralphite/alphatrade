"""Paper trading 账本。JSONL 留痕，悲观成交模型。名义资金 $100k。

文件：
  ledger/events.jsonl    审计流水（signal/order/fill/exit/mark 全记录，只追加）
  ledger/positions.json  当前持仓
  ledger/trades.jsonl    已平仓交易（含完整入出场与成本）
"""
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LED = ROOT / "ledger"
LED.mkdir(exist_ok=True)
EVENTS = LED / "events.jsonl"
POSITIONS = LED / "positions.json"
TRADES = LED / "trades.jsonl"

NOTIONAL = 100_000.0
POS_PCT = 0.02          # 单仓 2%
MAX_POS_PCT = 0.03      # 硬上限 3%
MAX_NEW_PER_DAY = 15
STOP_PCT = 0.04         # -4% 止损
HOLD_DAYS = 2           # T+2 收盘退出


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_event(kind: str, payload: dict):
    rec = {"ts": now_iso(), "kind": kind, **payload}
    with EVENTS.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def load_positions() -> dict:
    if POSITIONS.exists():
        return json.loads(POSITIONS.read_text())
    return {}


def save_positions(pos: dict):
    POSITIONS.write_text(json.dumps(pos, indent=1, ensure_ascii=False))


def slippage_bps(price: float, adv_dollars: float) -> float:
    """悲观滑点：流动性好 15bps，小/低价 25bps（PROJECT.md 成本模型）。"""
    if price < 10 or (adv_dollars or 0) < 5e7:
        return 25.0
    return 15.0


def commission(shares: float) -> float:
    return max(1.0, shares * 0.005)


def open_position(ticker: str, ref_price: float, adv: float, signal: dict) -> dict:
    """按成交模型买入。ref_price 必须是信号产生之后拉取的最新价。"""
    pos = load_positions()
    if ticker in pos:
        return {"error": "already-holding"}
    today = now_iso()[:10]
    opened_today = sum(1 for p in pos.values() if p["entry_ts"][:10] == today)
    opened_today += sum(1 for L in _read_jsonl(TRADES) if L.get("entry_ts", "")[:10] == today)
    if opened_today >= MAX_NEW_PER_DAY:
        return {"error": "daily-open-limit"}
    gross = sum(p["shares"] * p["entry_px"] for p in pos.values())
    if gross + NOTIONAL * POS_PCT > NOTIONAL:
        return {"error": "gross-limit"}

    slip = slippage_bps(ref_price, adv)
    fill_px = ref_price * (1 + slip / 1e4)
    shares = int((NOTIONAL * POS_PCT) / fill_px)
    if shares <= 0:
        return {"error": "too-expensive"}
    fee = commission(shares)
    p = {
        "pos_id": str(uuid.uuid4())[:8],
        "ticker": ticker,
        "shares": shares,
        "entry_px": round(fill_px, 4),
        "entry_ref_px": ref_price,
        "entry_slip_bps": slip,
        "entry_fee": round(fee, 2),
        "entry_ts": now_iso(),
        "stop_px": round(fill_px * (1 - STOP_PCT), 4),
        "exit_after_close_n": HOLD_DAYS,
        "signal": signal,
    }
    pos[ticker] = p
    save_positions(pos)
    log_event("fill_open", p)
    return p


def close_position(ticker: str, ref_price: float, adv: float, reason: str) -> dict:
    pos = load_positions()
    p = pos.pop(ticker, None)
    if not p:
        return {"error": "no-position"}
    slip = slippage_bps(ref_price, adv)
    fill_px = ref_price * (1 - slip / 1e4)
    fee = commission(p["shares"])
    pnl = (fill_px - p["entry_px"]) * p["shares"] - fee - p["entry_fee"]
    trade = {
        **p,
        "exit_px": round(fill_px, 4),
        "exit_ref_px": ref_price,
        "exit_slip_bps": slip,
        "exit_fee": round(fee, 2),
        "exit_ts": now_iso(),
        "exit_reason": reason,
        "pnl": round(pnl, 2),
        "ret_net": round(pnl / (p["entry_px"] * p["shares"]), 6),
    }
    save_positions(pos)
    with TRADES.open("a") as f:
        f.write(json.dumps(trade, ensure_ascii=False) + "\n")
    log_event("fill_close", trade)
    return trade


def _read_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def summary() -> dict:
    trades = _read_jsonl(TRADES)
    pos = load_positions()
    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] <= 0]
    gross_win = sum(t["pnl"] for t in wins)
    gross_loss = -sum(t["pnl"] for t in losses)
    return {
        "closed_trades": len(trades),
        "open_positions": len(pos),
        "total_pnl": round(sum(t["pnl"] for t in trades), 2),
        "win_rate": round(len(wins) / len(trades), 3) if trades else None,
        "profit_factor": round(gross_win / gross_loss, 3) if gross_loss > 0 else None,
        "avg_ret_bps": round(1e4 * sum(t["ret_net"] for t in trades) / len(trades), 1) if trades else None,
    }


if __name__ == "__main__":
    print(json.dumps(summary(), indent=1))
