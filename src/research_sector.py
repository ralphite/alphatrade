"""H7 行业 ETF 横截面轮动矩阵回测。日频信号、低成本（5bps 双边）、2 年窗口。

Universe：11 SPDR 行业 + 6 高流动行业/主题 ETF。
信号族（预先定义全报告，防挑参数）：
  R1  1日反转：昨日收益最弱 k 只等权做多，持 1 天
  R5  5日反转：5日累计最弱 k 只，持 1 天
  M20 20日动量：最强 k 只，持 1 天
  M60 60日动量：最强 k 只，持 5 天（每 5 天调仓）
k ∈ {2,3}。全部相对 SPY 超额、扣调仓成本（换手份额 × 5bps）。

用法：.venv/bin/python src/research_sector.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402

ETFS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC",
        "SMH", "XBI", "KRE", "ITB", "XOP", "GDX"]
COST_BPS = 5.0


def load_panel():
    px = {}
    for t in ETFS + ["SPY"]:
        df = daily_history(t, period="3y")
        px[t] = df["Close"]
    panel = pd.DataFrame(px).dropna()
    return panel[panel.index >= panel.index[-505]]  # ~2年


def run_strategy(panel, lookback, top_k, reverse, hold, label):
    rets = panel.pct_change()
    spy = rets["SPY"]
    uni = [c for c in panel.columns if c != "SPY"]
    sig = panel[uni].pct_change(lookback)
    daily_ex, turn_cost_total = [], 0.0
    prev_hold = set()
    dates = list(panel.index)
    for i in range(max(lookback + 1, 61), len(dates) - 1):
        if (i - 61) % hold != 0:
            # 持有期内沿用上次持仓
            d_next = dates[i + 1]
            if prev_hold:
                r = rets.loc[d_next, list(prev_hold)].mean() - spy.loc[d_next]
                daily_ex.append(r * 1e4)
            continue
        d, d_next = dates[i], dates[i + 1]
        s = sig.loc[d].dropna()
        if len(s) < 10:
            continue
        picks = set((s.nsmallest(top_k) if reverse else s.nlargest(top_k)).index)
        turnover = len(picks - prev_hold) / top_k if prev_hold else 1.0
        cost = turnover * 2 * COST_BPS / hold  # 双边成本摊到持有期
        r = rets.loc[d_next, list(picks)].mean() - spy.loc[d_next]
        daily_ex.append(r * 1e4 - cost)
        prev_hold = picks
    v = daily_ex
    n = len(v)
    m = sum(v) / n
    var = sum((x - m) ** 2 for x in v) / (n - 1)
    se = (var / n) ** 0.5
    ann = m * 252 / 1e4
    print(f"{label:22s} n={n:4d}天 净超额={m:+6.2f}bps/天 t={m/se:+5.2f} 年化超额={ann:+7.1%} win={sum(1 for x in v if x>0)/n:.0%}")


def main():
    panel = load_panel()
    print(f"=== 行业 ETF 轮动矩阵（{panel.index[0].date()}..{panel.index[-1].date()}，{len(ETFS)} ETF，成本 {COST_BPS}bps/边×换手）===")
    for k in (2, 3):
        run_strategy(panel, 1, k, True, 1, f"R1  1日反转 top{k}")
        run_strategy(panel, 5, k, True, 1, f"R5  5日反转 top{k}")
        run_strategy(panel, 20, k, False, 1, f"M20 20日动量 top{k}")
        run_strategy(panel, 60, k, False, 5, f"M60 60日动量 top{k} 持5天")


if __name__ == "__main__":
    main()
