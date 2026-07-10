"""执行信号：读 signals/<date>/signals.jsonl，对 direction=long & conviction=3 且未执行的开仓。

用法：.venv/bin/python src/execute_signals.py signals/2026-07-10/signals.jsonl"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data import snapshot  # noqa: E402
from ledger import EVENTS, _read_jsonl, load_positions, log_event, open_position  # noqa: E402


def executed_signal_ids():
    return {e.get("signal", {}).get("signal_id") for e in _read_jsonl(EVENTS) if e.get("kind") == "fill_open"}


def main(path):
    signals = [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
    done = executed_signal_ids()
    pos = load_positions()
    results = []
    for s in signals:
        log_event("signal", s)
        if s.get("direction") != "long" or s.get("conviction") != 3:
            continue
        if s["signal_id"] in done:
            results.append((s["ticker"], "already-executed"))
            continue
        if s["ticker"] in pos:
            results.append((s["ticker"], "already-holding"))
            continue
        try:
            snap = snapshot(s["ticker"])
        except Exception as e:  # noqa: BLE001
            results.append((s["ticker"], f"no-price:{e}"))
            continue
        adv = s.get("adv_dollars") or (snap.get("avg_vol_10d") or 0) * snap["last"]
        r = open_position(s["ticker"], snap["last"], adv, s)
        pos = load_positions()
        results.append((s["ticker"], r.get("error") or f"OPEN {r['shares']}sh @ {r['entry_px']}"))
    for t, msg in results:
        print(f"{t:6s} {msg}")
    if not results:
        print("no executable signals (need direction=long & conviction=3)")


if __name__ == "__main__":
    main(sys.argv[1])
