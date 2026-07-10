"""H4c 大盘 ETF 日历窗口回测：turn-of-month (TOM) 效应。免费日线，微成本（2bps/边）。

TOM 定义（文献经典）：每月最后 Nl 个交易日收盘买入，次月第 Nf 个交易日收盘卖出。
对照：非 TOM 时段持有。基准：buy&hold。
扫描 (Nl, Nf) ∈ {1..4}×{1..5}，报告最优与稳健性（防过拟合：看参数面是否平滑）。

用法：.venv/bin/python src/research_calendar.py QQQ SPY IWM
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402

COST_SIDE_BPS = 2.0


def tom_mask(idx, nl, nf):
    """返回布尔序列：位于 TOM 窗口（月末 nl 天 + 月初 nf 天）的持有日。
    持有区间 = [月末第-nl个交易日收盘, 次月第nf个交易日收盘] 之间的每日收益。"""
    s = pd.Series(idx, index=idx)
    month = s.dt.to_period("M")
    # 每月交易日序号（正向与反向）
    fwd = month.groupby(month).cumcount() + 1
    rev = month[::-1].groupby(month[::-1]).cumcount()[::-1] + 1
    return (rev <= nl) | (fwd <= nf)


def run(ticker):
    df = daily_history(ticker, period="7y")
    df = df[df.index >= "2020-07-01"].copy()
    ret = df["Close"].pct_change().dropna()
    idx = ret.index
    print(f"\n=== {ticker} TOM 扫描 2020-07..now（{len(ret)} 交易日）===")
    bh_ann = float(ret.mean() * 252)
    print(f"buy&hold 年化 {bh_ann:+.1%}")
    best = None
    grid = {}
    for nl in range(1, 5):
        for nf in range(1, 6):
            m = tom_mask(idx, nl, nf)
            # 持有 TOM 日的收益；每月一进一出 → 成本 = 12 次双边/年
            r = ret[m.values]
            ann = float(r.mean() * 252 * len(r) / len(ret))  # 按实际持有天数折算贡献
            hold_frac = len(r) / len(ret)
            ann_net = float(r.sum() / (len(ret) / 252)) - 12 * 2 * COST_SIDE_BPS / 1e4
            n_month = len(ret) / 21
            per_month_bps = r.sum() / n_month * 1e4 - 4
            sr = float(r.mean() / r.std() * (252 * hold_frac) ** 0.5) if r.std() > 0 else 0
            grid[(nl, nf)] = per_month_bps
            if best is None or ann_net > best[2]:
                best = (nl, nf, ann_net, per_month_bps, hold_frac, sr)
    nl, nf, ann_net, pm, hf, sr = best
    print(f"最优 (月末{nl}天,月初{nf}天): 净年化 {ann_net:+.1%} | {pm:+.0f}bps/月 | 持有占比 {hf:.0%} | 粗Sharpe {sr:.2f}")
    # 参数面稳健性：最优邻域均值
    neigh = [grid.get((nl + a, nf + b)) for a in (-1, 0, 1) for b in (-1, 0, 1) if grid.get((nl + a, nf + b)) is not None]
    print(f"邻域均值 {sum(neigh)/len(neigh):+.0f}bps/月（{len(neigh)} 参数点）| 全网格均值 {sum(grid.values())/len(grid):+.0f}bps/月")
    # 非 TOM 对照
    m = tom_mask(idx, nl, nf)
    r_out = ret[~m.values]
    print(f"对照（非TOM时段，{1-hf:.0%} 时间）: 年化贡献 {float(r_out.sum()/(len(ret)/252)):+.1%}")
    return grid


if __name__ == "__main__":
    for t in sys.argv[1:]:
        run(t)
