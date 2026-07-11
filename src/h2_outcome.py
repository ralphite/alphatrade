"""H2 预检收益判定：transcript 信号 → T+2 开盘入场（规避 headline 定价与过冲期）→ T+22 收盘。

分层：forward_signal=long ／ guidance=raise但未达long ／ tone<=-1（负语气组，反向检验）／ 其余 skip。
一切池内差分。成本：单程滑点按市值分层（无市值数据用 35bps 中档）+ 佣金。

用法：.venv/bin/python src/h2_outcome.py（读 research/h2_screen/signals_part_*.jsonl）
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history  # noqa: E402
from ledger import commission  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "h2_screen"
SLIP = 35.0
HOLD = 20
ENTRY_LAG = 2  # 财报日后第 2 个交易日开盘


def simulate(sig, spy):
    tkr = sig["ticker"]
    try:
        df = daily_history(tkr, period="1y")
    except Exception:  # noqa: BLE001
        return None
    df = df.copy()
    df.index = df.index.strftime("%Y-%m-%d")
    cal = list(df.index)
    rd = sig["report_date"][:10]
    fwd = [c for c in cal if c > rd]
    if len(fwd) < ENTRY_LAG + HOLD + 1:
        return None
    ed = fwd[ENTRY_LAG - 1]
    xd = fwd[ENTRY_LAG - 1 + HOLD]
    entry = float(df.loc[ed, "Open"]) * (1 + SLIP / 1e4)
    exitp = float(df.loc[xd, "Close"]) * (1 - SLIP / 1e4)
    shares = int(2000 / entry)
    if shares <= 0:
        return None
    ret = (exitp - entry) / entry - 2 * commission(shares) / (entry * shares)
    try:
        spy_ret = float(spy.loc[xd, "Close"]) / float(spy.loc[ed, "Open"]) - 1
    except Exception:  # noqa: BLE001
        spy_ret = 0.0
    return (ret - spy_ret) * 1e4


def stats(vals):
    if not vals:
        return "n=0"
    n = len(vals)
    m = sum(vals) / n
    var = sum((x - m) ** 2 for x in vals) / (n - 1) if n > 1 else 0
    se = (var / n) ** 0.5 if var > 0 else float("inf")
    med = sorted(vals)[n // 2]
    return f"n={n:3d} avg={m:+7.1f}bps med={med:+7.1f} t={m/se if se>0 else 0:+5.2f} win={sum(1 for x in vals if x>0)/n:.0%}"


def main():
    sigs = []
    for p in sorted(DIR.glob("signals_part_*.jsonl")):
        for line in p.read_text().splitlines():
            if line.strip():
                sigs.append(json.loads(line))
    spy = daily_history("SPY", period="1y").copy()
    spy.index = spy.index.strftime("%Y-%m-%d")
    rows = []
    for s in sigs:
        ex = simulate(s, spy)
        if ex is not None:
            rows.append({**s, "excess": ex})
    allv = [r["excess"] for r in rows]
    pm = sum(allv) / len(allv) if allv else 0
    print(f"=== H2 预检 outcome（T+{ENTRY_LAG} 开盘入场，持 {HOLD}td，池均值 {pm:+.1f}bps）===")
    layers = {
        "long 信号(raise+tone+qa)": [r["excess"] - pm for r in rows if r.get("forward_signal") == "long"],
        "guidance=raise 全体":      [r["excess"] - pm for r in rows if r.get("guidance_action") == "raise"],
        "tone>=+1 全体":            [r["excess"] - pm for r in rows if (r.get("tone") or 0) >= 1],
        "tone<=-1(负语气,反检)":     [r["excess"] - pm for r in rows if (r.get("tone") or 0) <= -1],
        "guidance=lower(反检)":     [r["excess"] - pm for r in rows if r.get("guidance_action") == "lower"],
        "skip 对照":                [r["excess"] - pm for r in rows if r.get("forward_signal") == "skip"],
    }
    for k, v in layers.items():
        print(f"{k:24s} {stats(v)}")
    (DIR / "outcomes.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
