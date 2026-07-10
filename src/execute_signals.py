"""执行信号（红队修复版）。

规则：
  - conviction=3 & long & 未 veto → 执行开仓（占风控额度）
  - 其余非 skip（conv1/2、3-vetoed）→ 影子开仓（不占额度，纯记录）
  - would-short 标注 → 影子 short 开仓
  - 一切成交用 fresh_price（时间戳校验，P1-5），同时记 SPY 参考价（P0-1）
  - Day-0 warmup 批次：信号带 "warmup": true，正常成交但不入正式统计

用法：.venv/bin/python src/execute_signals.py signals/2026-07-10/signals.jsonl"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data import fresh_price  # noqa: E402
from ledger import EVENTS, _read_jsonl, load_positions, log_event, open_position  # noqa: E402


def spy_ref():
    return fresh_price("SPY")["price"]


def already_opened():
    ids = set()
    for e in _read_jsonl(EVENTS):
        if e.get("kind") in ("fill_open", "fill_open_shadow"):
            ids.add((e.get("signal", {}).get("signal_id"), e.get("shadow", False)))
    return ids


def main(path):
    signals = [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
    done = already_opened()
    try:
        spy = spy_ref()
    except Exception as e:  # noqa: BLE001
        print(f"ABORT: no fresh SPY price ({e}) — market closed?")
        return
    results = []
    for s in signals:
        log_event("signal", s)
        direction = s.get("direction")
        conv = s.get("conviction")
        vetoed = s.get("vetoed", False)
        note = s.get("note") or ""
        # would-short 检测需排除否定句（"不作would-short"/"not would-short"）
        would_short = bool(re.search(r"(?<![不非未])(?:^|[\s,;:。，'\"(（])would-short", note)) \
            and not re.search(r"(?:不作|不标|不做|并非|不是|not?\s+|no\s+)would-short", note)
        execute = direction == "long" and conv == 3 and not vetoed
        shadow_long = direction == "long" and not execute
        shadow_short = would_short
        if not (execute or shadow_long or shadow_short):
            continue
        try:
            fp = fresh_price(s["ticker"])
        except Exception as e:  # noqa: BLE001
            results.append((s["ticker"], f"no-fresh-price: {e}"))
            log_event("no_fresh_price", {"ticker": s["ticker"], "signal_id": s.get("signal_id"), "err": str(e)})
            continue
        meta = {"market_cap": s.get("market_cap"), "spread_bps": fp.get("spread_bps"), "quote_ts": fp["quote_ts"]}
        if execute:
            if (s.get("signal_id"), False) in done:
                results.append((s["ticker"], "already-executed"))
                continue
            r = open_position(s["ticker"], fp["price"], meta, s, spy, shadow=False, direction="long")
            results.append((s["ticker"], r.get("error") or f"OPEN {r['shares']}sh @ {r['entry_px']} (slip {r['entry_slip_bps']}bps)"))
        else:
            d = "short" if shadow_short and not shadow_long else "long"
            if (s.get("signal_id"), True) in done:
                results.append((s["ticker"], "shadow-already"))
                continue
            r = open_position(s["ticker"], fp["price"], meta, s, spy, shadow=True, direction=d)
            results.append((s["ticker"], r.get("error") or f"SHADOW-{d.upper()} {r['shares']}sh @ {r['entry_px']}"))
    for t, msg in results:
        print(f"{t:6s} {msg}")
    if not results:
        print("no actionable signals")


if __name__ == "__main__":
    main(sys.argv[1])
