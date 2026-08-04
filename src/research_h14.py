"""H14 关卡 1:backwardation 做多波动(VIXY)。预注册判据见 HYPOTHESES.md。

规则(冻结):昨收 ^VIX >= ^VIX3M -> 今日持有 VIXY;否则现金。成本 10bps/边。
输出:池内差分 / 净期望 / 三段分解 / 极端日审计 / 相关性。
"""
import math
import sys
import numpy as np
import pandas as pd
import yfinance as yf

COST_BPS = 10.0  # 单边,悲观
SEGMENTS = [("2011-2015", "2011-01-01", "2015-12-31"),
            ("2016-2020", "2016-01-01", "2020-12-31"),
            ("2021-2026", "2021-01-01", "2026-12-31")]
EXTREME = ["2018-02-05", "2020-02-24", "2020-03-16", "2024-08-05", "2025-04-07"]


def load():
    px = {}
    for sym in ["^VIX", "^VIX3M", "VIXY", "QQQ"]:
        h = yf.Ticker(sym).history(start="2010-12-01", end="2026-08-04", auto_adjust=True)["Close"]
        h.index = pd.to_datetime([d.strftime("%Y-%m-%d") for d in h.index])
        px[sym] = h
    df = pd.DataFrame(px).dropna(subset=["^VIX", "^VIX3M", "VIXY"])
    df["vixy_ret"] = df["VIXY"].pct_change()
    df["qqq_ret"] = df["QQQ"].pct_change()
    # 信号:昨收倒挂 -> 今日在场(严格无 lookahead)
    df["backw"] = (df["^VIX"] >= df["^VIX3M"]).shift(1).fillna(False)
    return df.dropna(subset=["vixy_ret"])


def strat_returns(df):
    """含换手成本的策略日收益。进出场各扣 COST_BPS。"""
    inpos = df["backw"].values
    r = df["vixy_ret"].values.copy()
    out = np.where(inpos, r, 0.0)
    prev = np.concatenate([[False], inpos[:-1]])
    turn = (inpos != prev)  # 状态切换日:进场或离场各一次成本
    out = out - turn * (COST_BPS / 1e4)
    return pd.Series(out, index=df.index)


def ann(series):
    if len(series) == 0:
        return float("nan")
    return (1 + series).prod() ** (252 / len(series)) - 1


class _W:
    def __init__(self, statistic, pvalue):
        self.statistic, self.pvalue = statistic, pvalue


def welch_t(a, b):
    """Welch 两样本 t + 正态近似双尾 p(样本量大,足够)。"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    t = (a.mean() - b.mean()) / np.sqrt(va + vb)
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return _W(t, p)


def tstat(x):
    x = np.asarray(x, dtype=float)
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 and x.std() > 0 else float("nan")


def main():
    df = load()
    print(f"样本 {df.index[0].date()} .. {df.index[-1].date()}  n={len(df)}  在场天数={int(df['backw'].sum())} "
          f"({df['backw'].mean()*100:.1f}%)")

    # --- 判据 1:池内差分 ---
    ind = df.loc[df["backw"], "vixy_ret"]
    allr = df["vixy_ret"]
    outd = df.loc[~df["backw"], "vixy_ret"]
    diff = ind.mean() - allr.mean()
    # 差分显著性:两样本 Welch t(在场 vs 不在场)更严格
    welch = welch_t(ind, outd)
    print("\n[判据1 池内差分]")
    print(f"  倒挂日均 {ind.mean()*1e4:+.1f}bps (n={len(ind)}) | 全样本 {allr.mean()*1e4:+.1f}bps | "
          f"非倒挂 {outd.mean()*1e4:+.1f}bps")
    print(f"  差分(vs 全样本) {diff*1e4:+.1f}bps | Welch t(在场 vs 不在场) = {welch.statistic:.2f} "
          f"(p={welch.pvalue:.4f}) | 单样本 t(在场日均≠0) = {tstat(ind):.2f}")

    # --- 判据 2:净期望 ---
    s = strat_returns(df)
    print("\n[判据2 含成本净期望]")
    print(f"  策略年化 {ann(s)*100:+.2f}%  | 累计 {((1+s).prod()-1)*100:+.1f}%  | "
          f"VIXY 买入持有年化 {ann(df['vixy_ret'])*100:+.2f}%")
    inmkt = s[df["backw"].values]
    print(f"  单位在场时间:策略在场日均 {inmkt.mean()*1e4:+.1f}bps(含成本摊销) | "
          f"在场天数 {len(inmkt)} | 年化(仅在场时间口径) {ann(inmkt)*100:+.2f}%")
    sd = s.std() * np.sqrt(252)
    print(f"  Sharpe(全时间口径) {ann(s)/sd if sd > 0 else float('nan'):.2f} | 年化波动 {sd*100:.1f}% | "
          f"最大回撤 {((1+s).cumprod()/(1+s).cumprod().cummax()-1).min()*100:.1f}%")

    # --- 判据 3:三段分解 ---
    print("\n[判据3 三段分解]")
    for name, a, b in SEGMENTS:
        m = (df.index >= a) & (df.index <= b)
        sub, ss = df[m], s[m]
        if sub["backw"].sum() < 5:
            print(f"  {name}: 样本不足")
            continue
        d = sub.loc[sub['backw'], 'vixy_ret'].mean() - sub['vixy_ret'].mean()
        print(f"  {name}: 差分 {d*1e4:+7.1f}bps | 策略年化 {ann(ss)*100:+7.2f}% | "
              f"在场 {int(sub['backw'].sum())}d ({sub['backw'].mean()*100:.0f}%) | "
              f"在场日均 {sub.loc[sub['backw'],'vixy_ret'].mean()*1e4:+.1f}bps")

    # --- 判据 4:极端日审计 ---
    print("\n[判据4 极端日审计(冲击日是否在场)]")
    for d in EXTREME:
        ts = pd.Timestamp(d)
        if ts not in df.index:
            print(f"  {d}: 非交易日")
            continue
        row = df.loc[ts]
        print(f"  {d}: {'在场' if row['backw'] else '空仓'} | VIXY {row['vixy_ret']*100:+.1f}% | "
              f"QQQ {row['qqq_ret']*100:+.1f}% | VIX {row['^VIX']:.1f}/{row['^VIX3M']:.1f}")
    # 危机月整体表现
    print("\n  危机窗口累计(策略 vs QQQ):")
    for name, a, b in [("2018-02", "2018-01-29", "2018-02-12"), ("2020-02/03", "2020-02-19", "2020-03-31"),
                       ("2024-08", "2024-07-31", "2024-08-09"), ("2025-04", "2025-04-02", "2025-04-15")]:
        m = (df.index >= a) & (df.index <= b)
        print(f"    {name}: 策略 {((1+s[m]).prod()-1)*100:+.1f}%  QQQ {((1+df.loc[m,'qqq_ret']).prod()-1)*100:+.1f}%"
              f"  (在场 {int(df.loc[m,'backw'].sum())}/{int(m.sum())}d)")

    # --- 判据 5:相关性 ---
    print("\n[判据5 对冲属性]")
    q = df["qqq_ret"]
    print(f"  corr(策略日收益, QQQ) = {np.corrcoef(s, q)[0,1]:+.3f}")
    print(f"  QQQ 下跌日(<-1%)策略日均 {s[q < -0.01].mean()*1e4:+.1f}bps (n={int((q<-0.01).sum())}) | "
          f"QQQ 上涨日(>+1%)策略日均 {s[q > 0.01].mean()*1e4:+.1f}bps")
    # 与 H12(SVXY 在 contango 在场)天然互斥,检查是否真的不重叠
    print(f"  与 H12 在场日重叠 = {int((df['backw'] & ~df['backw']).sum())} (设计上互斥)")

    s.to_csv("research/h14_strategy_returns.csv", header=["ret"])
    print("\n[saved research/h14_strategy_returns.csv]")


if __name__ == "__main__":
    sys.exit(main())
