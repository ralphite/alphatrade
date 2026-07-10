"""关卡 1 历史粗筛：对 knowledge-cutoff 之后的历史窗口跑同一套过滤 + 评估管线。

无 lookahead 设计：
  - 窗口必须晚于评估模型的 knowledge cutoff（2026-01）→ 评估者不知道结局
  - 决策时点模拟"事件后次日盘前"：评估者只见事件前价格数据（chg_since_event_pct=None）
  - 流动性过滤用事件前日线（liquidity_gate event_date 已保证）
  - 不污染 forward 流程的 seen_8k.txt

用法：.venv/bin/python src/research_screen.py 2026-06-09 2026-06-11
输出：research/screen_<start>_<end>/queue.json + batch_*.json
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data import liquidity_gate  # noqa: E402
from edgar import acceptance_time, fetch_filing_text, parse_hit, search_8k  # noqa: E402
from scan_8k import BORING_ONLY, INTERESTING  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main(startdt, enddt, batch_size=9):
    out_dir = ROOT / "research" / f"screen_{startdt}_{enddt}"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = [parse_hit(h) for h in search_8k(startdt, enddt, max_pages=40)]
    by_adsh = {}
    for h in raw:
        cur = by_adsh.setdefault(h["adsh"], {**h, "docs": []})
        if h.get("doc"):
            cur["docs"].append(h["doc"])
    hits = list(by_adsh.values())
    stats = {"total_filings": len(hits), "item_pass": 0, "ticker_pass": 0, "gate_pass": 0, "no_content": 0}
    queue = []
    for h in hits:
        items = set(h["items"])
        if not (items & INTERESTING) or items <= BORING_ONLY:
            continue
        stats["item_pass"] += 1
        t = h["ticker"]
        if not t or "-" in t or len(t) > 5:
            continue
        stats["ticker_pass"] += 1
        ok, snap, reason = liquidity_gate(t, event_date=h["file_date"])
        if not ok:
            continue
        stats["gate_pass"] += 1
        try:
            doc = fetch_filing_text(h["cik"], h["adsh"], docs=h.get("docs"))
        except Exception as e:  # noqa: BLE001
            print(f"  text-fail {t}: {e}")
            continue
        if len(doc["text"]) < 1200 and "item" not in doc["text"].lower():
            stats["no_content"] += 1
            continue
        queue.append({
            "signal_id": h["adsh"],
            "ticker": t,
            "company": h["company"],
            "items": sorted(items),
            "file_date": h["file_date"],
            "accepted": acceptance_time(h["cik"], h["adsh"]),
            "market_cap": snap.get("market_cap"),   # 注意：这是当前市值，仅用于滑点分档近似
            "prev_close": snap.get("prev_close"),
            "last_price": None,                      # 决策时点=次日盘前，不给事件后价格
            "chg_since_event_pct": None,
            "adv_dollars": snap.get("adv_dollars"),
            "text": doc["text"],
            "research_window": f"{startdt}..{enddt}",
        })
        time.sleep(0.15)
    (out_dir / "queue.json").write_text(json.dumps(queue, ensure_ascii=False, indent=1))
    n_batches = max(1, (len(queue) + batch_size - 1) // batch_size)
    for i in range(n_batches):
        b = queue[i::n_batches]
        (out_dir / f"batch_{i}.json").write_text(json.dumps(b, ensure_ascii=False, indent=1))
    print(json.dumps({**stats, "queued": len(queue), "batches": n_batches, "dir": str(out_dir)}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
