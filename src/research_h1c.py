"""H1c 历史模拟：盘后即时入场（公告后 ≥30min 的第一个盘后 15m bar）vs H1 v1 的次日开盘入场。

范围：两窗口全部 direction=long 信号中，accepted 在 16:00–19:30 ET 的（盘后公告）。
成交假设（悲观）：盘后入场滑点 200bps（mcap<$500M 300bps）；
退出 A=次日开盘（-60bps 卖出滑点，纯 gap 捕获）；退出 B=T+2 close（-60bps，与 v1 可比）。
SPY 基准用日线（入场日 close → 退出日 close 近似）。

用法：.venv/bin/python src/research_h1c.py research/screen_A/signals.jsonl research/screen_B/signals.jsonl
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402

ET = ZoneInfo("America/New_York")


def ah_entry_bar(ticker, accepted_utc):
    """公告(UTC)+30min 后的第一个盘后 15m bar。返回 (bar_time_et, price) 或 None。"""
    acc = datetime.fromisoformat(accepted_utc.replace("Z", "+00:00")).astimezone(ET)
    if not (16 <= acc.hour < 20 or (acc.hour == 15 and acc.minute >= 55)):
        return None  # 只测盘后公告
    day = acc.strftime("%Y-%m-%d")
    nxt = (acc + timedelta(days=2)).strftime("%Y-%m-%d")
    try:
        df = yf.Ticker(ticker).history(start=day, end=nxt, interval="15m", prepost=True)
    except Exception:  # noqa: BLE001
        return None
    if df is None or df.empty:
        return None
    df = df.tz_convert(ET) if df.index.tz else df
    cutoff = acc + timedelta(minutes=30)
    same_day_ah = df[(df.index >= cutoff) & (df.index.strftime("%Y-%m-%d") == day) & (df.index.hour >= 16) & (df.index.hour < 20)]
    if same_day_ah.empty:
        return None
    bar = same_day_ah.iloc[0]
    px = float(bar["Close"] if bar["Close"] > 0 else bar["Open"])
    return (str(same_day_ah.index[0]), px)


def simulate_signal(s, spy):
    tkr = s["ticker"]
    r = ah_entry_bar(tkr, s.get("accepted") or "")
    if not r:
        return None
    bar_ts, raw_px = r
    slip_in = 300 if (s.get("market_cap") or 0) < 5e8 else 200
    entry_px = raw_px * (1 + slip_in / 1e4)
    try:
        d = daily_history(tkr, period="6mo").copy()
    except Exception:  # noqa: BLE001
        return None
    d.index = d.index.strftime("%Y-%m-%d")
    cal = list(d.index)
    day = bar_ts[:10]
    fwd = [c for c in cal if c > day]
    if len(fwd) < 3:
        return None
    open_day, t2_day = fwd[0], fwd[2]
    exit_open = float(d.loc[open_day, "Open"]) * (1 - 60 / 1e4)
    exit_t2 = float(d.loc[t2_day, "Close"]) * (1 - 60 / 1e4)
    retA = exit_open / entry_px - 1
    retB = exit_t2 / entry_px - 1
    try:
        spyA = float(spy.loc[open_day, "Open"]) / float(spy.loc[day, "Close"]) - 1
        spyB = float(spy.loc[t2_day, "Close"]) / float(spy.loc[day, "Close"]) - 1
    except Exception:  # noqa: BLE001
        spyA = spyB = 0.0
    return {
        "ticker": tkr, "conviction": s.get("conviction"), "entry_bar": bar_ts,
        "entry_px": round(entry_px, 4), "gap_exit_open": round(exit_open, 4),
        "exA_gap_excess_bps": round((retA - spyA) * 1e4, 1),
        "exB_t2_excess_bps": round((retB - spyB) * 1e4, 1),
    }


def stats(vals):
    if not vals:
        return {"n": 0}
    n = len(vals)
    m = sum(vals) / n
    var = sum((x - m) ** 2 for x in vals) / (n - 1) if n > 1 else 0
    se = (var / n) ** 0.5 if n > 1 and var > 0 else float("inf")
    return {"n": n, "avg_bps": round(m, 1), "t": round(m / se, 2) if se > 0 else None,
            "win": round(sum(1 for x in vals if x > 0) / n, 3)}


def main(paths):
    spy = daily_history("SPY", period="6mo").copy()
    spy.index = spy.index.strftime("%Y-%m-%d")
    rows = []
    for p in paths:
        for line in Path(p).read_text().splitlines():
            if not line.strip():
                continue
            s = json.loads(line)
            if s.get("direction") != "long":
                continue
            r = simulate_signal(s, spy)
            if r:
                rows.append(r)
                print(f"{r['ticker']:6s} conv{r['conviction']} entry {r['entry_bar'][:16]} @ {r['entry_px']}  gapEx {r['exA_gap_excess_bps']:+.0f}  t2Ex {r['exB_t2_excess_bps']:+.0f}")
    out = Path("research/h1c_results.jsonl")
    out.write_text("\n".join(json.dumps(r) for r in rows))
    print()
    for conv in (3, 2, None):
        sub = [r for r in rows if (r["conviction"] == conv if conv else True)]
        label = f"conv{conv}" if conv else "ALL-long"
        print(f"{label:9s} 盘后入场→次日开盘(gap): {json.dumps(stats([r['exA_gap_excess_bps'] for r in sub]))}")
        print(f"{'':9s} 盘后入场→T+2 close:      {json.dumps(stats([r['exB_t2_excess_bps'] for r in sub]))}")


if __name__ == "__main__":
    main(sys.argv[1:])
