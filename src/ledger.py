"""Paper trading 账本。JSONL 留痕，悲观成交模型，一切指标以对 SPY 的 excess 为准。

文件：
  ledger/events.jsonl          审计流水（signal/order/fill/exit/mark 全记录，只追加）
  ledger/positions.json        当前执行持仓（conv3 通过 red-team 的）
  ledger/trades.jsonl          已平仓执行交易
  ledger/shadow_positions.json 影子持仓（conv1/2、3-vetoed、would-short；不占风控额度）
  ledger/shadow_trades.jsonl   已平仓影子交易

红队修复（2026-07-10）：
  P0-1 每笔记录同窗口 SPY 收益，excess = ret_net - spy_ret
  P0-2 滑点按章程：max(spread*0.5, 10bps)，小盘(<$500M 或 spread>30bps)翻倍；无 spread 用市值分层 floor
  P1-7 影子信号跑同一套成交/退出，分层对照
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LED = ROOT / "ledger"
LED.mkdir(exist_ok=True)
EVENTS = LED / "events.jsonl"
POSITIONS = LED / "positions.json"
TRADES = LED / "trades.jsonl"
SHADOW_POS = LED / "shadow_positions.json"
SHADOW_TRADES = LED / "shadow_trades.jsonl"

ET = ZoneInfo("America/New_York")
NOTIONAL = 100_000.0
POS_PCT = 0.02
MAX_NEW_PER_DAY = 15
STOP_PCT = 0.04
HOLD_DAYS = 2


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def et_date():
    return datetime.now(ET).strftime("%Y-%m-%d")


def log_event(kind: str, payload: dict):
    rec = {"ts": now_iso(), "et_date": et_date(), "kind": kind, **payload}
    with EVENTS.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def _load(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(path: Path, obj: dict):
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False))


def _read_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def slippage_bps(price: float, market_cap, spread_bps=None) -> float:
    """章程口径：max(50% spread, 10bps)；小盘（<$500M 或 spread>30bps）翻倍。
    无实时 spread 时用市值分层的保守 floor（小盘事件后 spread 宽，宁可悲观）。"""
    if spread_bps and spread_bps > 0:
        s = max(spread_bps * 0.5, 10.0)
        if (market_cap or 0) < 5e8 or spread_bps > 30:
            s *= 2
        return min(s, 300.0)
    mc = market_cap or 0
    if mc >= 2e9:
        base = 15.0
    elif mc >= 5e8:
        base = 35.0
    else:
        base = 60.0
    if price < 10:
        base += 10.0
    return base


def commission(shares: float) -> float:
    return max(1.0, shares * 0.005)


def _fill(side: str, ref_price: float, price_meta: dict) -> tuple:
    slip = slippage_bps(ref_price, price_meta.get("market_cap"), price_meta.get("spread_bps"))
    px = ref_price * (1 + slip / 1e4) if side == "buy" else ref_price * (1 - slip / 1e4)
    return round(px, 4), slip


def open_position(ticker: str, ref_price: float, price_meta: dict, signal: dict,
                  spy_ref: float, shadow=False, direction="long") -> dict:
    """price_meta: {market_cap, spread_bps?, quote_ts}。ref_price 必须是信号之后的新鲜价（P1-5 由调用方保证）。"""
    book_path = SHADOW_POS if shadow else POSITIONS
    book = _load(book_path)
    key = f"{ticker}:{signal.get('signal_id','')}" if shadow else ticker
    if key in book:
        return {"error": "already-holding"}
    if not shadow:
        today = et_date()
        opened = sum(1 for p in book.values() if p["et_open_date"] == today)
        opened += sum(1 for t in _read_jsonl(TRADES) if t.get("et_open_date") == today)
        if opened >= MAX_NEW_PER_DAY:
            return {"error": "daily-open-limit"}
        gross = sum(p["shares"] * p["entry_px"] for p in book.values())
        if gross + NOTIONAL * POS_PCT > NOTIONAL:
            return {"error": "gross-limit"}
    side = "buy" if direction == "long" else "sell"
    fill_px, slip = _fill(side, ref_price, price_meta)
    shares = int((NOTIONAL * POS_PCT) / fill_px)
    if shares <= 0:
        return {"error": "too-expensive"}
    p = {
        "pos_id": str(uuid.uuid4())[:8],
        "ticker": ticker,
        "direction": direction,
        "shadow": shadow,
        "shares": shares,
        "entry_px": fill_px,
        "entry_ref_px": ref_price,
        "entry_slip_bps": slip,
        "entry_fee": round(commission(shares), 2),
        "entry_ts": now_iso(),
        "et_open_date": et_date(),
        "entry_quote_ts": price_meta.get("quote_ts"),
        "spy_entry": spy_ref,
        "stop_px": round(fill_px * (1 - STOP_PCT), 4) if direction == "long" else round(fill_px * (1 + STOP_PCT), 4),
        "exit_after_close_n": HOLD_DAYS,
        "signal": signal,
    }
    book[key] = p
    _save(book_path, book)
    log_event("fill_open_shadow" if shadow else "fill_open", p)
    return p


def close_position(key: str, ref_price: float, price_meta: dict, reason: str,
                   spy_ref: float, shadow=False) -> dict:
    book_path = SHADOW_POS if shadow else POSITIONS
    trades_path = SHADOW_TRADES if shadow else TRADES
    book = _load(book_path)
    p = book.pop(key, None)
    if not p:
        return {"error": "no-position"}
    side = "sell" if p["direction"] == "long" else "buy"
    fill_px, slip = _fill(side, ref_price, price_meta)
    fee = commission(p["shares"])
    sign = 1 if p["direction"] == "long" else -1
    pnl = sign * (fill_px - p["entry_px"]) * p["shares"] - fee - p["entry_fee"]
    ret_net = pnl / (p["entry_px"] * p["shares"])
    spy_ret = (spy_ref / p["spy_entry"] - 1) if (spy_ref and p.get("spy_entry")) else None
    excess = (ret_net - sign * spy_ret) if spy_ret is not None else None
    trade = {
        **p,
        "exit_px": fill_px,
        "exit_ref_px": ref_price,
        "exit_slip_bps": slip,
        "exit_fee": round(fee, 2),
        "exit_ts": now_iso(),
        "et_close_date": et_date(),
        "exit_reason": reason,
        "spy_exit": spy_ref,
        "spy_ret": round(spy_ret, 6) if spy_ret is not None else None,
        "pnl": round(pnl, 2),
        "ret_net": round(ret_net, 6),
        "excess_ret": round(excess, 6) if excess is not None else None,
    }
    _save(book_path, book)
    with trades_path.open("a") as f:
        f.write(json.dumps(trade, ensure_ascii=False) + "\n")
    log_event("fill_close_shadow" if shadow else "fill_close", trade)
    return trade


def load_positions(shadow=False) -> dict:
    return _load(SHADOW_POS if shadow else POSITIONS)


def _stats(trades):
    if not trades:
        return {"n": 0}
    wins = [t for t in trades if t["pnl"] > 0]
    gw = sum(t["pnl"] for t in wins)
    gl = -sum(t["pnl"] for t in trades if t["pnl"] <= 0)
    ex = [t["excess_ret"] for t in trades if t.get("excess_ret") is not None]
    out = {
        "n": len(trades),
        "total_pnl": round(sum(t["pnl"] for t in trades), 2),
        "win_rate": round(len(wins) / len(trades), 3),
        "profit_factor": round(gw / gl, 3) if gl > 0 else None,
        "avg_ret_bps": round(1e4 * sum(t["ret_net"] for t in trades) / len(trades), 1),
    }
    if ex:
        n = len(ex)
        mean = sum(ex) / n
        var = sum((x - mean) ** 2 for x in ex) / (n - 1) if n > 1 else 0.0
        se = (var / n) ** 0.5 if n > 1 else float("inf")
        out.update({
            "avg_excess_bps": round(1e4 * mean, 1),
            "excess_t_stat": round(mean / se, 2) if se > 0 else None,
            "excess_pf": _excess_pf(ex),
        })
    return out


def _excess_pf(ex):
    gw = sum(x for x in ex if x > 0)
    gl = -sum(x for x in ex if x <= 0)
    return round(gw / gl, 3) if gl > 0 else None


def summary() -> dict:
    trades = _read_jsonl(TRADES)
    shadow = _read_jsonl(SHADOW_TRADES)
    by_conv = {}
    for t in shadow:
        k = f"conv{t['signal'].get('conviction')}/{t['direction']}" + ("-vetoed" if t['signal'].get('vetoed') else "")
        by_conv.setdefault(k, []).append(t)
    return {
        "executed": _stats(trades),
        "open_positions": len(load_positions()),
        "open_shadows": len(load_positions(shadow=True)),
        "shadow_by_layer": {k: _stats(v) for k, v in sorted(by_conv.items())},
    }


if __name__ == "__main__":
    print(json.dumps(summary(), indent=1, ensure_ascii=False))
