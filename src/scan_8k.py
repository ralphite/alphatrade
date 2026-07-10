"""扫描 EDGAR 新 8-K → 过滤（item / ticker / 流动性）→ 拉全文 → 写评估队列。

用法：.venv/bin/python src/scan_8k.py [startdt] [enddt]   （默认：昨天..今天，ET）
输出：queue/pending_<ts>.json + 更新 data/seen_8k.txt
评估队列由 Claude（loop agent）按 prompts/eval_8k_v1.md 逐条评估后写 signals/。"""
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from data import liquidity_gate  # noqa: E402
from edgar import acceptance_time, fetch_filing_text, parse_hit, search_8k  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SEEN = ROOT / "data" / "seen_8k.txt"
QUEUE = ROOT / "queue"
QUEUE.mkdir(exist_ok=True)

# 有方向性信息含量的 item（HYPOTHESES.md H1 信号定义 v1）
INTERESTING = {"1.01", "1.02", "2.01", "2.02", "4.02", "5.02", "7.01", "8.01"}
# 纯程序性 item 组合直接跳过（只有 5.07 股东会 / 9.01 exhibit 之类）
BORING_ONLY = {"5.07", "9.01", "5.03", "3.03"}


def load_seen():
    if SEEN.exists():
        return set(SEEN.read_text().split())
    return set()


def main(startdt=None, enddt=None):
    et_now = datetime.now(ZoneInfo("America/New_York"))
    enddt = enddt or et_now.strftime("%Y-%m-%d")
    startdt = startdt or (et_now - timedelta(days=1)).strftime("%Y-%m-%d")
    seen = load_seen()
    raw = [parse_hit(h) for h in search_8k(startdt, enddt)]
    # efts 是文档级索引：同一 filing 的本体/exhibit 各一条 hit。按 adsh 合并，收集全部文档名。
    by_adsh = {}
    for h in raw:
        cur = by_adsh.setdefault(h["adsh"], {**h, "docs": []})
        if h.get("doc"):
            cur["docs"].append(h["doc"])
    hits = list(by_adsh.values())
    stats = {"total": len(hits), "new": 0, "item_pass": 0, "ticker_pass": 0, "gate_pass": 0}
    candidates = []
    for h in hits:
        if h["adsh"] in seen:
            continue
        stats["new"] += 1
        items = set(h["items"])
        if not (items & INTERESTING) or items <= BORING_ONLY:
            seen.add(h["adsh"])
            continue
        stats["item_pass"] += 1
        t = h["ticker"]
        if not t or "-" in t or len(t) > 5:
            seen.add(h["adsh"])
            continue
        stats["ticker_pass"] += 1
        candidates.append(h)

    queue = []
    for h in candidates:
        ok, snap, reason = liquidity_gate(h["ticker"], event_date=h["file_date"])
        seen.add(h["adsh"])
        if not ok:
            continue
        stats["gate_pass"] += 1
        try:
            doc = fetch_filing_text(h["cik"], h["adsh"], docs=h.get("docs"))
        except Exception as e:  # noqa: BLE001
            print(f"  text-fail {h['ticker']} {h['adsh']}: {e}")
            continue
        # 红队 P1-3：抓不到实质正文的不要塞给评估者
        if len(doc["text"]) < 1200 and "item" not in doc["text"].lower():
            stats["no_content"] = stats.get("no_content", 0) + 1
            continue
        queue.append({
            "signal_id": h["adsh"],
            "ticker": h["ticker"],
            "company": h["company"],
            "items": sorted(set(h["items"])),
            "file_date": h["file_date"],
            "accepted": acceptance_time(h["cik"], h["adsh"]),  # P1-1 分钟级
            "market_cap": snap.get("market_cap"),
            "prev_close": snap.get("prev_close"),              # 事件前收盘
            "last_price": snap.get("last"),
            "chg_since_event_pct": snap.get("chg_since_event_pct"),  # P1-2 喂给 priced-in 判断
            "adv_dollars": snap.get("adv_dollars"),            # P1-4 事件前 ADV
            "text": doc["text"],
        })
        time.sleep(0.2)

    SEEN.write_text("\n".join(sorted(seen)))
    out = None
    if queue:
        out = QUEUE / f"pending_{et_now.strftime('%Y%m%d_%H%M%S')}.json"
        out.write_text(json.dumps(queue, ensure_ascii=False, indent=1))
    print(json.dumps({"window": [startdt, enddt], **stats, "queued": len(queue),
                      "queue_file": str(out) if out else None}, ensure_ascii=False))


if __name__ == "__main__":
    a = sys.argv[1:]
    main(*a[:2])
