"""H0 校准回测：QQQ/SPY 隔夜 vs 日内 vs buy-and-hold，2020-2026。
目的：验证数据层与成本模型，对照已知文献结论（隔夜收益占优）。不是 alpha 策略。"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402

COST_PER_SIDE_BPS = 2.0  # 大盘 ETF spread ~1bp，取悲观 2bps/边


def run(ticker: str, start="2020-01-01"):
    df = daily_history(ticker, period="7y")
    df = df[df.index >= start].copy()
    o, c = df["Open"], df["Close"]
    prev_c = c.shift(1)
    overnight = (o / prev_c - 1).dropna()           # 昨收 -> 今开
    intraday = (c / o - 1).dropna()                 # 今开 -> 今收
    cost = COST_PER_SIDE_BPS / 1e4
    on_net = overnight - 2 * cost                   # 每晚一进一出
    id_net = intraday - 2 * cost

    def stats(r: pd.Series, label: str):
        cum = float((1 + r).prod() - 1)
        ann = float(r.mean() * 252)
        vol = float(r.std() * 252 ** 0.5)
        sharpe = ann / vol if vol > 0 else float("nan")
        return {"leg": label, "n": len(r), "cum_ret": round(cum, 3),
                "ann_ret": round(ann, 3), "ann_vol": round(vol, 3), "sharpe": round(sharpe, 2)}

    bh = (c / prev_c - 1).dropna()
    rows = [
        stats(on_net, f"{ticker} overnight(net)"),
        stats(id_net, f"{ticker} intraday(net)"),
        stats(bh, f"{ticker} buy&hold(gross)"),
    ]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = pd.concat([run("QQQ"), run("SPY")], ignore_index=True)
    print(out.to_string(index=False))
    out.to_csv(Path(__file__).parent.parent / "reports" / "h0_calibration.csv", index=False)
