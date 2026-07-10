"""H4b 隔夜横截面回测：close→open 持有，小中盘池（5 窗口 queue 的全部 ticker）。

变体：
  A 全池等权基线
  B 前日日内输家（open→close 跌幅前 20%）——文献：日内输家隔夜反弹更强
  C 前日日内赢家（对照）
成本：双边滑点（ADV 分档同 ledger 模型）+ 佣金——隔夜策略每天一轮双边，成本是生死线。
输出毛/净对照，直接呈现成本影响。

用法：.venv/bin/python src/research_overnight.py 2026-01-02 2026-07-01
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402
from ledger import slippage_bps  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def universe():
    seen = set()
    for q in ROOT.glob("research/screen_*/queue.json"):
        for x in json.loads(q.read_text()):
            seen.add(x["ticker"])
    return sorted(seen)


def stats(vals):
    if not vals:
        return "n=0"
    n = len(vals)
    m = sum(vals) / n
    var = sum((x - m) ** 2 for x in vals) / (n - 1) if n > 1 else 0
    se = (var / n) ** 0.5 if var > 0 else float("inf")
    ann = m * 252 / 1e4
    return f"n={n:5d} avg={m:+7.2f}bps/晚 t={m/se if se>0 else 0:+5.2f} 年化={ann:+.1%}"


def main(start, end):
    tickers = universe()
    print(f"universe: {len(tickers)} tickers (from screened queues)")
    rows = []
    for i, t in enumerate(tickers):
        try:
            df = daily_history(t, period="1y")
        except Exception:  # noqa: BLE001
            continue
        df = df.copy()
        df.index = df.index.strftime("%Y-%m-%d")
        df = df[(df.index >= start) & (df.index <= end)]
        if len(df) < 30:
            continue
        adv = float((df["Close"] * df["Volume"]).mean())
        if adv < 2e6 or float(df["Close"].iloc[-1]) < 3:
            continue
        mcap_proxy = 3e9 if adv > 5e7 else (1e9 if adv > 1e7 else 4e8)
        slip = slippage_bps(float(df["Close"].mean()), mcap_proxy)
        o, c = df["Open"], df["Close"]
        on_gross = (o.shift(-1) / c - 1).dropna() * 1e4          # 今收→明开
        intraday_prev = (c / o - 1) * 1e4                         # 当日日内（作为次日信号）
        for day, g in on_gross.items():
            rows.append({"day": day, "t": t, "gross": float(g),
                         "net": float(g) - 2 * slip - 2,          # 双边滑点+佣金≈2bps
                         "prev_intraday": float(intraday_prev.loc[day])})
        if (i + 1) % 150 == 0:
            print(f"  {i+1}/{len(tickers)}", flush=True)
    df = pd.DataFrame(rows)
    print(f"\n=== 隔夜横截面 {start}..{end}（{df['t'].nunique()} 股票 × {df['day'].nunique()} 晚）===")
    print("A 全池等权   毛:", stats(list(df["gross"])))
    print("A 全池等权   净:", stats(list(df["net"])))
    # 按日分组取日内输家/赢家前20%
    lose, win = [], []
    for day, g in df.groupby("day"):
        q20 = g["prev_intraday"].quantile(0.2)
        q80 = g["prev_intraday"].quantile(0.8)
        lose.extend(g[g["prev_intraday"] <= q20]["net"])
        win.extend(g[g["prev_intraday"] >= q80]["net"])
    print("B 日内输家20% 净:", stats(lose))
    print("C 日内赢家20% 净:", stats(win))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
