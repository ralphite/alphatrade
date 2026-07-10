"""H7 日内模式地图：QQQ/SPY 的时段结构系统扫描。成本假设：4bps 双边（大盘 ETF）。

第一部分（2 年 1h bars）：各小时时段平均收益 → 时段地图
第二部分（60 天 15m bars）：
  P1 开盘动量：09:30-10:00 方向 → 10:00-16:00 同向持有
  P2 尾盘动量（杠杆再平衡流）：09:30-15:30 累计方向 → 15:30-16:00 同向
  P3 隔夜 gap fade：|gap|>0.3% → 开盘反向持有 30min
  P4 午间反转：11:30-13:30 方向 → 13:30-15:30 反向
每个模式输出：n、毛 avg bps、净 avg bps（-4bps）、t、win、按 |信号强度| 分层。

用法：.venv/bin/python src/research_intraday.py QQQ
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import yfinance as yf  # noqa: E402

COST = 4.0  # bps 双边


def stats(vals, label):
    if len(vals) == 0:
        print(f"{label:36s} n=0")
        return
    n = len(vals)
    m = sum(vals) / n
    var = sum((x - m) ** 2 for x in vals) / (n - 1) if n > 1 else 0
    se = (var / n) ** 0.5 if var > 0 else float("inf")
    win = sum(1 for x in vals if x > 0) / n
    print(f"{label:36s} n={n:4d} 毛={m:+7.2f} 净={m-COST:+7.2f}bps t(毛)={m/se if se>0 else 0:+5.2f} win={win:.0%}")


def hourly_map(ticker):
    df = yf.Ticker(ticker).history(period="730d", interval="1h")
    df = df.tz_convert("America/New_York")
    df["ret"] = df["Close"] / df["Open"] - 1
    print(f"=== {ticker} 小时时段地图（{df.index[0].date()}..{df.index[-1].date()}）===")
    for h, g in df.groupby(df.index.hour):
        if 9 <= h <= 15:
            r = list(g["ret"] * 1e4)
            stats(r, f"  {h:02d}:30 bar 持有1h")


def m15(ticker):
    df = yf.Ticker(ticker).history(period="60d", interval="15m")
    df = df.tz_convert("America/New_York")
    days = {}
    for day, g in df.groupby(df.index.strftime("%Y-%m-%d")):
        g = g.between_time("09:30", "16:00")
        if len(g) < 20:
            continue
        days[day] = g
    keys = sorted(days)
    print(f"\n=== {ticker} 15m 模式（{len(keys)} 天）===")

    def seg(g, t1, t2):
        s = g.between_time(t1, t2)
        if s.empty:
            return None
        return float(s["Close"].iloc[-1] / s["Open"].iloc[0] - 1) * 1e4

    p1, p2, p2s, p3, p4 = [], [], [], [], []
    prev_close = None
    for day in keys:
        g = days[day]
        o930 = float(g["Open"].iloc[0])
        r_open30 = seg(g, "09:30", "09:59")
        r_rest = seg(g, "10:00", "15:59")
        r_day_to_1530 = (float(g.between_time("15:15", "15:29")["Close"].iloc[-1]) / o930 - 1) * 1e4 \
            if not g.between_time("15:15", "15:29").empty else None
        r_last30 = seg(g, "15:30", "15:59")
        r_mid = seg(g, "11:30", "13:29")
        r_pm = seg(g, "13:30", "15:29")
        if r_open30 is not None and r_rest is not None:
            p1.append(r_rest if r_open30 > 0 else -r_rest)
        if r_day_to_1530 is not None and r_last30 is not None:
            v = r_last30 if r_day_to_1530 > 0 else -r_last30
            p2.append(v)
            if abs(r_day_to_1530) > 100:
                p2s.append(v)
        if prev_close is not None and r_open30 is not None:
            gap = (o930 / prev_close - 1) * 1e4
            if abs(gap) > 30:
                p3.append(-r_open30 if gap > 0 else r_open30)
        if r_mid is not None and r_pm is not None:
            p4.append(-r_pm if r_mid > 0 else r_pm)
        prev_close = float(g["Close"].iloc[-1])
    stats(p1, "P1 开盘30m动量→持有到收盘")
    stats(p2, "P2 尾盘动量(日内方向→15:30-16:00)")
    stats(p2s, "P2s 同上·仅|日内|>1% 的日子")
    stats(p3, "P3 隔夜gap>0.3% 开盘反向30m")
    stats(p4, "P4 午间方向→午后反向")


if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "QQQ"
    hourly_map(t)
    m15(t)
