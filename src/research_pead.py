"""H4-PEAD pilot：gap-based 财报后漂移（微/小盘）。纯规则，无 LLM。

信号：2.02 财报 8-K → 反应日 D（accepted 16:00 前=当日，否则次日）→
      反应幅度 R = D 收盘 / 事件前收盘 - 1。
      R > +5%（大 beat 代理）→ D+1 开盘买入，持 HOLD_TD 交易日，止损 -8%（日线 Low 穿越）。
分层对照：R < -5%（做多则为反向检验）、|R| < 2%（无惊喜对照）。
成本：滑点市值分层（ledger.slippage_bps）+ 佣金；池内差分 = 减去全池均值。

用法：.venv/bin/python src/research_pead.py 2026-03-01 2026-05-31 [hold_td=20]
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402
from edgar import acceptance_time, parse_hit, search_8k  # noqa: E402
from ledger import commission, slippage_bps  # noqa: E402

ET = ZoneInfo("America/New_York")
STOP_DN = 0.08
POS = 2000.0
ROOT = Path(__file__).resolve().parent.parent


def reaction_day(accepted_utc, cal):
    dt = datetime.fromisoformat(accepted_utc.replace("Z", "+00:00")).astimezone(ET)
    d = dt.strftime("%Y-%m-%d")
    if dt.hour < 16 and d in cal:
        return d
    nxt = [c for c in cal if c > d]
    return nxt[0] if nxt else None


def simulate(tkr, accepted, spy, hold_td):
    try:
        df = daily_history(tkr, period="1y")
    except Exception:  # noqa: BLE001
        return None
    df = df.copy()
    df.index = df.index.strftime("%Y-%m-%d")
    cal = list(df.index)
    D = reaction_day(accepted, cal)
    if not D or D not in df.index:
        return None
    dpos = cal.index(D)
    if dpos < 21 or dpos + 1 + hold_td >= len(cal):
        return None
    pre = df.iloc[dpos - 21:dpos]
    adv = float((pre["Close"] * pre["Volume"]).mean())
    prev_close = float(df.iloc[dpos - 1]["Close"])
    if prev_close < 3 or adv < 2e6:
        return None
    R = float(df.loc[D, "Close"]) / prev_close - 1
    entry_day = cal[dpos + 1]
    # 滑点分档用 ADV 代理市值：ADV>$50M 按大盘档(15bps)，$10-50M 中档(35)，其余小盘档(60)
    mcap_proxy = 3e9 if adv > 5e7 else (1e9 if adv > 1e7 else 4e8)
    slip = slippage_bps(float(df.loc[entry_day, "Open"]), mcap_proxy)
    entry_px = float(df.loc[entry_day, "Open"]) * (1 + slip / 1e4)
    stop_px = entry_px * (1 - STOP_DN)
    epos = dpos + 1
    exit_day, exit_px, reason = None, None, None
    for i in range(epos, min(epos + hold_td + 1, len(cal))):
        day = cal[i]
        op, lo = float(df.loc[day, "Open"]), float(df.loc[day, "Low"])
        ref = op if i > epos else entry_px
        if ref <= stop_px or lo <= stop_px:
            exit_day, reason = day, "stop"
            exit_px = min(op, stop_px) if i > epos else stop_px
            break
    if exit_day is None:
        exit_day = cal[min(epos + hold_td, len(cal) - 1)]
        exit_px = float(df.loc[exit_day, "Close"])
        reason = "time"
    exit_px *= (1 - slip / 1e4)
    shares = int(POS / entry_px)
    if shares <= 0:
        return None
    fees = 2 * commission(shares)
    ret = (exit_px - entry_px) / entry_px - fees / (entry_px * shares)
    try:
        spy_ret = float(spy.loc[exit_day, "Close"]) / float(spy.loc[entry_day, "Open"]) - 1
    except Exception:  # noqa: BLE001
        spy_ret = 0.0
    return {"ticker": tkr, "D": D, "R_pct": round(R * 100, 2), "entry": entry_day,
            "exit": exit_day, "reason": reason,
            "excess_bps": round((ret - spy_ret) * 1e4, 1)}


def stats(vals):
    if not vals:
        return "n=0"
    n = len(vals)
    m = sum(vals) / n
    var = sum((x - m) ** 2 for x in vals) / (n - 1) if n > 1 else 0
    se = (var / n) ** 0.5 if var > 0 else float("inf")
    med = sorted(vals)[n // 2]
    return f"n={n:4d} avg={m:+8.1f}bps med={med:+8.1f} t={m/se if se>0 else 0:+5.2f} win={sum(1 for x in vals if x>0)/n:.0%}"


def main(startdt, enddt, hold_td=20):
    print(f"scanning 2.02 8-Ks {startdt}..{enddt} ...", flush=True)
    raw = [parse_hit(h) for h in search_8k(startdt, enddt, max_pages=100)]
    seen, events = set(), []
    for h in raw:
        if h["adsh"] in seen or not h["ticker"] or "-" in h["ticker"] or len(h["ticker"]) > 5:
            continue
        seen.add(h["adsh"])
        if "2.02" in (h["items"] or []):
            events.append(h)
    print(f"2.02 filings with ticker: {len(events)}", flush=True)
    spy = daily_history("SPY", period="1y").copy()
    spy.index = spy.index.strftime("%Y-%m-%d")
    rows, done = [], set()
    for i, h in enumerate(events):
        key = (h["ticker"], h["file_date"])
        if key in done:
            continue
        done.add(key)
        acc = acceptance_time(h["cik"], h["adsh"])
        if not acc:
            continue
        r = simulate(h["ticker"], acc, spy, hold_td)
        if r:
            rows.append(r)
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(events)} processed, {len(rows)} simulated", flush=True)
    out = ROOT / "research" / f"pead_{startdt}_{enddt}.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in rows))
    allv = [r["excess_bps"] for r in rows]
    pool_mean = sum(allv) / len(allv) if allv else 0
    print(f"\n=== gap-based PEAD {startdt}..{enddt} hold={hold_td}td (excess vs SPY) ===")
    print("全池       :", stats(allv))
    for name, lo, hi in [("大beat R>+5%", 5, 999), ("小beat 2..5%", 2, 5), ("无惊喜 |R|<2%", -2, 2),
                          ("小miss -5..-2", -5, -2), ("大miss R<-5%", -999, -5)]:
        sub = [r["excess_bps"] for r in rows if lo < r["R_pct"] <= hi]
        subd = [v - pool_mean for v in sub]
        print(f"{name:14s}:", stats(sub), "| 池内差分:", stats(subd).split('avg=')[1].split(' med')[0] if sub else "n=0")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], int(a[2]) if len(a) > 2 else 20)
