"""H5 验证：5.02（高管变动）8-K 后的次日开盘做多漂移。纯规则信号（不经 LLM）。

规则：item 含 5.02 的 filing（gate 已过流动性），次日开盘买入，T+2 close 卖出，-4% 止损。
复用 research_outcome.simulate 的成交/成本模型。对照 = 同窗口非 5.02 池。

用法：.venv/bin/python src/research_h5.py <screen_dir> [...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402
from research_outcome import simulate  # noqa: E402


def stats(vals):
    if not vals:
        return "n=0"
    n = len(vals)
    m = sum(vals) / n
    var = sum((x - m) ** 2 for x in vals) / (n - 1) if n > 1 else 0
    se = (var / n) ** 0.5 if var > 0 else float("inf")
    med = sorted(vals)[n // 2]
    return f"n={n:3d} avg={m:+7.1f}bps med={med:+7.1f} t={m/se if se>0 else 0:+5.2f} win={sum(1 for x in vals if x>0)/n:.0%}"


def main(dirs):
    spy = daily_history("SPY", period="6mo").copy()
    spy.index = spy.index.strftime("%Y-%m-%d")
    for dd in dirs:
        d = Path(dd)
        queue = json.loads((d / "queue.json").read_text())
        g502, rest = [], []
        for q in queue:
            o = simulate({"ticker": q["ticker"], "accepted": q.get("accepted"),
                          "market_cap": q.get("market_cap")}, spy)
            if "error" in o or o.get("excess_ret") is None:
                continue
            v = o["excess_ret"] * 1e4
            (g502 if "5.02" in (q.get("items") or []) else rest).append(v)
        pool_mean = (sum(g502) + sum(rest)) / (len(g502) + len(rest)) if (g502 or rest) else 0
        diff = [v - pool_mean for v in g502]
        print(f"--- {d.name} ---")
        print(f"  5.02 池 (绝对excess): {stats(g502)}")
        print(f"  非5.02 (绝对excess): {stats(rest)}")
        print(f"  5.02 池内差分:        {stats(diff)}")


if __name__ == "__main__":
    main(sys.argv[1:])
