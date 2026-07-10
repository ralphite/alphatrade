"""关卡 1 收益计算：对历史粗筛的评估信号计算 T+2 excess，分层统计。

成交假设（与 forward 规则对齐，悲观）：
  - entry 日 = accepted(ET) 当日 16:00 前 → 当日无法用（我们模拟盘前流程）→ 一律用 accepted 次日
    的交易日开盘价（accepted 16:00 后本来就只能次日）；再加滑点（市值分档买入）
  - 退出 = entry 日起第 2 个交易日收盘 - 卖出滑点；或先触 -4% 止损（日线 Low 穿越，按 min(Open, stop) 成交）
  - excess = ret_net − 同窗口 SPY（entry Open → exit Close）
用法：.venv/bin/python src/research_outcome.py research/screen_2026-06-09_2026-06-11/signals.jsonl
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402
from ledger import commission, slippage_bps  # noqa: E402

ET = ZoneInfo("America/New_York")
STOP_PCT = 0.04
HOLD_TD = 2
NOTIONAL_POS = 2000.0


def entry_trading_day(accepted_utc: str, cal):
    """accepted(UTC) → 模拟盘前评估流程的 entry 交易日（accepted ET 日的下一个交易日）。"""
    dt = datetime.fromisoformat(accepted_utc.replace("Z", "+00:00")).astimezone(ET)
    d = dt.strftime("%Y-%m-%d")
    nxt = [c for c in cal if c > d]
    return nxt[0] if nxt else None


def simulate(sig, spy):
    tkr = sig["ticker"]
    try:
        df = daily_history(tkr, period="6mo")
    except Exception as e:  # noqa: BLE001
        return {"error": f"no-data:{e}"}
    df = df.copy()
    df.index = df.index.strftime("%Y-%m-%d")
    cal = list(df.index)
    if not sig.get("accepted"):
        return {"error": "no-accepted-ts"}
    ed = entry_trading_day(sig["accepted"], cal)
    if not ed or ed not in df.index:
        return {"error": "no-entry-day"}
    epos = cal.index(ed)
    if epos + HOLD_TD >= len(cal):
        return {"error": "insufficient-forward-data"}
    slip = slippage_bps(float(df.loc[ed, "Open"]), sig.get("market_cap"))
    entry_px = float(df.loc[ed, "Open"]) * (1 + slip / 1e4)
    stop_px = entry_px * (1 - STOP_PCT)
    exit_day, exit_px, reason = None, None, None
    for i in range(epos, epos + HOLD_TD + 1):
        day = cal[i]
        lo = float(df.loc[day, "Low"])
        op = float(df.loc[day, "Open"])
        if (op if i > epos else entry_px) <= stop_px or lo <= stop_px:
            exit_day, reason = day, "stop"
            exit_px = min(op, stop_px) if i > epos else stop_px
            break
    if exit_day is None:
        exit_day = cal[epos + HOLD_TD]
        exit_px = float(df.loc[exit_day, "Close"])
        reason = "time"
    exit_px *= (1 - slip / 1e4)
    shares = int(NOTIONAL_POS / entry_px)
    if shares <= 0:
        return {"error": "too-expensive"}
    fees = 2 * commission(shares)
    ret = (exit_px - entry_px) / entry_px - fees / (entry_px * shares)
    try:
        spy_in = float(spy.loc[ed, "Open"])
        spy_out = float(spy.loc[exit_day, "Close"])
        spy_ret = spy_out / spy_in - 1
    except Exception:  # noqa: BLE001
        spy_ret = None
    return {
        "entry_day": ed, "entry_px": round(entry_px, 4), "exit_day": exit_day,
        "exit_px": round(exit_px, 4), "exit_reason": reason, "slip_bps": slip,
        "ret_net": round(ret, 6), "spy_ret": round(spy_ret, 6) if spy_ret is not None else None,
        "excess_ret": round(ret - spy_ret, 6) if spy_ret is not None else None,
    }


def layer_stats(rows):
    ex = [r["outcome"]["excess_ret"] for r in rows if r["outcome"].get("excess_ret") is not None]
    if not ex:
        return {"n": 0}
    n = len(ex)
    mean = sum(ex) / n
    var = sum((x - mean) ** 2 for x in ex) / (n - 1) if n > 1 else 0
    se = (var / n) ** 0.5 if n > 1 and var > 0 else float("inf")
    win = sum(1 for x in ex if x > 0)
    return {"n": n, "avg_excess_bps": round(mean * 1e4, 1), "t_stat": round(mean / se, 2) if se > 0 else None,
            "win_rate_ex": round(win / n, 3), "min_bps": round(min(ex) * 1e4), "max_bps": round(max(ex) * 1e4)}


def main(signals_path):
    sigs = [json.loads(x) for x in Path(signals_path).read_text().splitlines() if x.strip()]
    spy = daily_history("SPY", period="6mo").copy()
    spy.index = spy.index.strftime("%Y-%m-%d")
    rows, errors = [], {}
    for s in sigs:
        o = simulate(s, spy)
        if "error" in o:
            errors[o["error"].split(":")[0]] = errors.get(o["error"].split(":")[0], 0) + 1
            continue
        rows.append({**{k: s.get(k) for k in ("ticker", "signal_id", "direction", "conviction", "note")}, "outcome": o})
    out = Path(signals_path).with_name("outcomes.jsonl")
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
    import re
    ws = [r for r in rows if re.search(r"would-short", r.get("note") or "")
          and not re.search(r"(?:不作|不标|不做|并非|不是|not?\s+|no\s+)would-short", r.get("note") or "")]
    layers = {
        "conv3_long(executable)": [r for r in rows if r["direction"] == "long" and r["conviction"] == 3],
        "conv2_long(shadow)": [r for r in rows if r["direction"] == "long" and r["conviction"] == 2],
        "skip(control)": [r for r in rows if r["direction"] == "skip"],
        "would_short(inverse-check)": ws,
    }
    print(f"simulated {len(rows)}/{len(sigs)}  errors={errors}")
    for name, rs in layers.items():
        print(f"{name:28s} {json.dumps(layer_stats(rs))}")


if __name__ == "__main__":
    main(sys.argv[1])
