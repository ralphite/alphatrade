"""H8 回测器骨架：0DTE XSP/SPY iron condor，固定规则，严格成交假设。

固定规则（预注册，代码即规则）：
  - 每交易日 10:00 ET：卖 15Δ call + 卖 15Δ put，买 5Δ 翼（defined risk）
  - 持有到收盘现金结算（0DTE）
  - 成交：卖腿@bid，买腿@ask（绝不用 mid）；佣金 $0.65/合约 × 4 腿
  - 头寸规模：每日 1 组；最大亏损 = 翼宽 - 净收权利金

数据接口：
  - polygon 模式：需要 POLYGON_API_KEY（../agentrunner/.env），拉真实期权链快照 → go/no-go 判定用
  - synthetic 模式：从 SPY 日线合成 BS 定价（自测框架逻辑；输出标注 SYNTHETIC，禁止用于判定）

极端日审计（预注册）：2018-02-05, 2020-03-12, 2020-03-16, 2024-08-05 及回测期内 VIX 单日 +10 的日子，
单独输出当日 P&L 并检查 defined 最大亏损是否触发。

用法：
  .venv/bin/python src/h8_backtester.py synthetic 2024-01-01 2026-07-01
  .venv/bin/python src/h8_backtester.py polygon 2022-01-01 2026-07-01   (需 key)
"""
import json
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
COMMISSION_PER_LEG = 0.65
AUDIT_DAYS = {"2018-02-05", "2020-03-12", "2020-03-16", "2022-06-13", "2024-08-05", "2025-04-07"}


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bs_put(S, K, T, sigma, r=0.04):
    if T <= 0 or sigma <= 0:
        return max(K - S, 0.0)
    d1 = (math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)


def bs_call(S, K, T, sigma, r=0.04):
    return bs_put(S, K, T, sigma, r) + S - K * math.exp(-r * T)


def strike_at_delta(S, T, sigma, abs_delta, is_call):
    """数值反解 |delta| 对应行权价（BS，synthetic 模式用）。
    call: |Δ|=Φ(d1)，K↑→|Δ|↓；put: |Δ|=Φ(-d1)，K↑→|Δ|↑。"""
    lo, hi = S * 0.80, S * 1.20
    for _ in range(60):
        K = (lo + hi) / 2
        d1 = (math.log(S / K) + (0.04 + sigma * sigma / 2) * T) / (sigma * math.sqrt(T))
        cur = norm_cdf(d1) if is_call else norm_cdf(-d1)
        too_high = cur > abs_delta
        if is_call:
            lo, hi = (K, hi) if too_high else (lo, K)
        else:
            lo, hi = (lo, K) if too_high else (K, hi)
    return (lo + hi) / 2


def synthetic_chain(S_open, day_realized_vol):
    """SYNTHETIC：以已实现波动近似当日隐波（现实中 0DTE IV 更高，此处偏保守低估权利金）。"""
    T = 6.5 / 24 / 365
    sigma = max(day_realized_vol * 1.1, 0.08)
    legs = {}
    for name, delta, is_call in [("sc", 0.15, True), ("sp", 0.15, False), ("lc", 0.05, True), ("lp", 0.05, False)]:
        K = strike_at_delta(S_open, T, sigma, delta, is_call)
        mid = bs_call(S_open, K, T, sigma) if is_call else bs_put(S_open, K, T, sigma)
        half_spread = max(0.03, mid * 0.08)  # 合成 spread：8% 或 $0.03
        legs[name] = {"K": round(K, 0), "bid": max(mid - half_spread, 0.01), "ask": mid + half_spread}
    return legs


def run_synthetic(start, end):
    spy = daily_history("SPY", period="10y")
    spy = spy[(spy.index >= start) & (spy.index <= end)].copy()
    rv = spy["Close"].pct_change().rolling(10).std() * (252 ** 0.5)
    rows = []
    for i in range(11, len(spy)):
        day = spy.index[i].strftime("%Y-%m-%d")
        S_open, S_close = float(spy["Open"].iloc[i]), float(spy["Close"].iloc[i])
        legs = synthetic_chain(S_open, float(rv.iloc[i - 1]))
        credit = legs["sc"]["bid"] + legs["sp"]["bid"] - legs["lc"]["ask"] - legs["lp"]["ask"]
        payoff = -(max(S_close - legs["sc"]["K"], 0) - max(S_close - legs["lc"]["K"], 0)
                   + max(legs["sp"]["K"] - S_close, 0) - max(legs["lp"]["K"] - S_close, 0))
        pnl = (credit + payoff) * 100 - 4 * COMMISSION_PER_LEG
        wing = max(legs["lc"]["K"] - legs["sc"]["K"], legs["sp"]["K"] - legs["lp"]["K"])
        max_loss = (wing - credit) * 100 + 4 * COMMISSION_PER_LEG
        rows.append({"day": day, "pnl": round(pnl, 2), "credit": round(credit * 100, 0),
                     "max_loss": round(max_loss, 0)})
    df = pd.DataFrame(rows).set_index("day")
    out = ROOT / "research" / "h8_synthetic_run.csv"
    df.to_csv(out)
    p = df["pnl"]
    print("=== H8 SYNTHETIC 自测（禁止用于 go/no-go——合成 IV 低估真实 VRP 与尾部）===")
    print(f"n={len(p)} 日均 ${p.mean():.2f} win={(p>0).mean():.0%} 最差日 ${p.min():.0f} P5 ${p.quantile(0.05):.0f}")
    print(f"平均收权利金 ${df['credit'].mean():.0f} 平均最大亏损 ${df['max_loss'].mean():.0f}")
    audit = df[df.index.isin(AUDIT_DAYS)]
    if not audit.empty:
        print("极端日审计:")
        print(audit.to_string())
    print(f"[saved {out}]")


def run_polygon(start, end):
    key = None
    envp = ROOT.parent / "agentrunner" / ".env"
    if envp.exists():
        for line in envp.read_text().splitlines():
            if line.startswith("POLYGON_API_KEY"):
                key = line.split("=", 1)[1].strip()
    if not key:
        print("POLYGON_API_KEY 未配置（../agentrunner/.env）。等待用户批准 H8 数据订阅后运行。")
        return
    print("TODO: polygon 期权链历史实现（等 key 到位后完成此函数）")


if __name__ == "__main__":
    mode, start, end = sys.argv[1], sys.argv[2], sys.argv[3]
    (run_synthetic if mode == "synthetic" else run_polygon)(start, end)
