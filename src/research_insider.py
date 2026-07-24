"""Insider cluster buying 关卡 1 回测(预注册规则,2026-07-24)。

信号:data/insider_clusters.csv 的 signal_date(该日收盘后信号可见)。
入场:signal_date 后第一个交易日开盘;持有 20/60 交易日两层。
过滤(信号时点可见字段):max_trans_value_usd<=1e8;(cik,signal_date) 去重;signal_lag_days<=10;
     入场前 20 日均额 >$2M 且价格 >$3(成本墙纪律)。
成本:ledger 滑点分档(ADV 代理市值)双边 + 佣金。
对照:vs SPY 与 vs IWM(小盘公平基准)双口径;内部单调性分层(人数/CEOCFO/金额)。
用法:.venv/bin/python src/research_insider.py 2023-01-01 [hold_td]
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402
from ledger import commission, slippage_bps  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
POS = 2000.0


def stats(vals):
    n = len(vals)
    if n < 3:
        return f"n={n}"
    m = sum(vals) / n
    var = sum((x - m) ** 2 for x in vals) / (n - 1)
    se = (var / n) ** 0.5
    med = sorted(vals)[n // 2]
    return f"n={n:5d} avg={m:+7.1f}bps med={med:+7.1f} t={m/se:+5.2f} win={sum(1 for x in vals if x>0)/n:.0%}"


def main(start, hold_td=20):
    cl = pd.read_csv(ROOT / "data" / "insider_clusters.csv")
    cl = cl[cl["signal_date"] >= start]
    cl = cl[cl["max_trans_value_usd"] <= 1e8]
    cl = cl[cl["signal_lag_days"] <= 10]
    cl = cl.drop_duplicates(subset=["issuer_cik", "signal_date"])
    print(f"events after filters: {len(cl)} ({cl['ticker'].nunique()} tickers), window {start}..", flush=True)
    spy = daily_history("SPY", period="4y")["Close"]
    iwm = daily_history("IWM", period="4y")["Close"]
    for b in (spy, iwm):
        b.index = b.index.strftime("%Y-%m-%d")
    rows, fails = [], 0
    cache = {}
    for i, ev in enumerate(cl.itertuples()):
        t = ev.ticker
        try:
            if t not in cache:
                df = daily_history(t, period="4y").copy()
                df.index = df.index.strftime("%Y-%m-%d")
                cache[t] = df
            df = cache[t]
            cal = list(df.index)
            fwd = [c for c in cal if c > str(ev.signal_date)[:10]]
            if len(fwd) < hold_td + 2:
                continue
            ed, xd = fwd[0], fwd[hold_td]
            epos = cal.index(ed)
            if epos < 21:
                continue
            pre = df.iloc[epos - 21:epos - 1]
            adv = float((pre["Close"] * pre["Volume"]).mean())
            if adv < 2e6 or float(pre["Close"].iloc[-1]) < 3:
                continue
            mcap_proxy = 3e9 if adv > 5e7 else (1e9 if adv > 1e7 else 4e8)
            slip = slippage_bps(float(df.loc[ed, "Open"]), mcap_proxy)
            entry = float(df.loc[ed, "Open"]) * (1 + slip / 1e4)
            exitp = float(df.loc[xd, "Close"]) * (1 - slip / 1e4)
            sh = int(POS / entry)
            if sh <= 0:
                continue
            ret = (exitp - entry) / entry - 2 * commission(sh) / (entry * sh)
            try:
                spy_r = float(spy.loc[xd]) / float(spy.loc[ed]) - 1
                iwm_r = float(iwm.loc[xd]) / float(iwm.loc[ed]) - 1
            except Exception:  # noqa: BLE001
                continue
            rows.append({"ticker": t, "sig": str(ev.signal_date)[:10],
                         "n_ins": int(ev.n_insiders), "ceo_cfo": bool(ev.has_ceo_cfo),
                         "value": float(ev.total_value_usd), "adv": adv,
                         "ex_spy": (ret - spy_r) * 1e4, "ex_iwm": (ret - iwm_r) * 1e4})
        except Exception:  # noqa: BLE001
            fails += 1
        if (i + 1) % 300 == 0:
            print(f"  {i+1}/{len(cl)} done, {len(rows)} simulated, {fails} fails", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "research" / f"insider_bt_{start}_{hold_td}td.csv", index=False)
    print(f"\n=== insider cluster 关卡1({start}.., hold={hold_td}td, 悲观成本) ===")
    print("全体 vs SPY :", stats(list(out["ex_spy"])))
    print("全体 vs IWM :", stats(list(out["ex_iwm"])))
    med_v = out["value"].median()
    for name, sub in [("≥3人", out[out.n_ins >= 3]), ("=2人", out[out.n_ins == 2]),
                      ("含CEO/CFO", out[out.ceo_cfo]), ("无CEO/CFO", out[~out.ceo_cfo]),
                      (f"金额>中位({med_v/1e6:.1f}M)", out[out.value > med_v]),
                      ("金额<=中位", out[out.value <= med_v])]:
        print(f"{name:18s} vs IWM:", stats(list(sub["ex_iwm"])))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2023-01-01",
         int(sys.argv[2]) if len(sys.argv) > 2 else 20)
