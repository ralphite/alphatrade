"""H1b 完整模拟：做空「叙事型 8-K（1.01/7.01/8.01 非 2.02/5.02）× eval long (conv>=2 或指定)」。

规则（HYPOTHESES.md H1b v1）：
  - 次日开盘做空（卖出滑点 = long 模型同档）
  - T+2 close 回补（买入滑点），或上行止损 +4%（日线 High 穿越，按 max(Open, stop) 回补——gap-up 直接吃开盘价）
  - borrow：年化 10%（mcap>=$500M）/ 50%（<$500M，hard-to-borrow 悲观），按实际持有天数计
  - excess = ret_short_net − (−1)×SPY 同窗收益（做空的基准对冲是 +SPY，即报告 ret + spy_ret）

用法：.venv/bin/python src/research_h1b.py <screen_dir> [<screen_dir> ...]
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402
from ledger import commission, slippage_bps  # noqa: E402

ET = ZoneInfo("America/New_York")
STOP_UP = 0.04
HOLD_TD = 2
POS = 2000.0


def narrative(items):
    s = set(items or [])
    return bool(s & {"1.01", "7.01", "8.01"}) and not (s & {"2.02", "5.02"})


def entry_day_of(accepted_utc, cal):
    dt = datetime.fromisoformat(accepted_utc.replace("Z", "+00:00")).astimezone(ET)
    d = dt.strftime("%Y-%m-%d")
    nxt = [c for c in cal if c > d]
    return nxt[0] if nxt else None


def simulate_short(sig, spy):
    tkr = sig["ticker"]
    try:
        df = daily_history(tkr, period="6mo").copy()
    except Exception:  # noqa: BLE001
        return None
    df.index = df.index.strftime("%Y-%m-%d")
    cal = list(df.index)
    if not sig.get("accepted"):
        return None
    ed = entry_day_of(sig["accepted"], cal)
    if not ed or ed not in df.index:
        return None
    epos = cal.index(ed)
    if epos + HOLD_TD >= len(cal):
        return None
    slip = slippage_bps(float(df.loc[ed, "Open"]), sig.get("market_cap"))
    entry_px = float(df.loc[ed, "Open"]) * (1 - slip / 1e4)  # 卖出开仓
    stop_px = entry_px * (1 + STOP_UP)
    exit_day, exit_px, reason = None, None, None
    for i in range(epos, epos + HOLD_TD + 1):
        day = cal[i]
        hi = float(df.loc[day, "High"])
        op = float(df.loc[day, "Open"])
        ref = op if i > epos else entry_px
        if ref >= stop_px or hi >= stop_px:
            exit_day, reason = day, "stop"
            exit_px = max(op, stop_px) if i > epos else stop_px
            break
    if exit_day is None:
        exit_day = cal[epos + HOLD_TD]
        exit_px = float(df.loc[exit_day, "Close"])
        reason = "time"
    exit_px *= (1 + slip / 1e4)  # 买入回补
    shares = int(POS / entry_px)
    if shares <= 0:
        return None
    held = cal.index(exit_day) - epos + 1
    borrow_rate = 0.50 if (sig.get("market_cap") or 0) < 5e8 else 0.10
    borrow_cost = entry_px * shares * borrow_rate * held / 252
    fees = 2 * commission(shares) + borrow_cost
    pnl = (entry_px - exit_px) * shares - fees
    ret = pnl / (entry_px * shares)
    try:
        spy_ret = float(spy.loc[exit_day, "Close"]) / float(spy.loc[ed, "Open"]) - 1
    except Exception:  # noqa: BLE001
        spy_ret = 0.0
    return {"ticker": tkr, "conviction": sig.get("conviction"), "entry_day": ed,
            "exit_day": exit_day, "exit_reason": reason,
            "ret_net_bps": round(ret * 1e4, 1),
            "excess_bps": round((ret + spy_ret) * 1e4, 1)}  # short 的市场中性对照：+beta 补回


def stats(vals):
    if not vals:
        return "n=0"
    n = len(vals)
    m = sum(vals) / n
    var = sum((x - m) ** 2 for x in vals) / (n - 1) if n > 1 else 0
    se = (var / n) ** 0.5 if var > 0 else float("inf")
    med = sorted(vals)[n // 2]
    return f"n={n} avg={m:+.1f}bps med={med:+.1f} t={m/se if se>0 else 0:+.2f} win={sum(1 for x in vals if x>0)/n:.0%}"


def main(dirs):
    spy = daily_history("SPY", period="6mo").copy()
    spy.index = spy.index.strftime("%Y-%m-%d")
    rows = []
    for dd in dirs:
        d = Path(dd)
        items_map = {x["signal_id"]: x["items"] for x in json.loads((d / "queue.json").read_text())}
        for line in (d / "signals.jsonl").read_text().splitlines():
            if not line.strip():
                continue
            s = json.loads(line)
            if s.get("direction") != "long" or (s.get("conviction") or 0) < 1:
                continue
            if not narrative(items_map.get(s["signal_id"])):
                continue
            r = simulate_short(s, spy)
            if r:
                rows.append(r)
                print(f"{r['ticker']:6s} conv{r['conviction']} {r['entry_day']} -> {r['exit_day']} [{r['exit_reason']:4s}] net {r['ret_net_bps']:+7.1f} excess {r['excess_bps']:+7.1f}")
    Path("research/h1b_results.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    print()
    print("ALL   :", stats([r["excess_bps"] for r in rows]))
    print("conv>=2:", stats([r["excess_bps"] for r in rows if (r["conviction"] or 0) >= 2]))
    print("conv3 :", stats([r["excess_bps"] for r in rows if r["conviction"] == 3]))
    stops = [r for r in rows if r["exit_reason"] == "stop"]
    print(f"stopped out: {len(stops)}/{len(rows)}")


if __name__ == "__main__":
    main(sys.argv[1:])
