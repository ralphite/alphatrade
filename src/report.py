"""日终报告：账本汇总 + 持仓 + 信号统计 → reports/daily_<date>.md 并打印。"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from ledger import EVENTS, SHADOW_TRADES, TRADES, _read_jsonl, load_positions, summary  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main():
    et = datetime.now(ZoneInfo("America/New_York"))
    today = et.strftime("%Y-%m-%d")
    events = _read_jsonl(EVENTS)
    sig_today = [e for e in events if e["kind"] == "signal" and e["ts"][:10] == today]
    exec_today = [e for e in events if e["kind"] == "fill_open" and e["ts"][:10] == today]
    closed_today = [t for t in _read_jsonl(TRADES) if t["exit_ts"][:10] == today]
    closed_today += [t for t in _read_jsonl(SHADOW_TRADES) if t.get("et_close_date") == today]
    pos = load_positions()
    s = summary()
    conv = {}
    for e in sig_today:
        k = f"conv{e.get('conviction')}/{e.get('direction')}"
        conv[k] = conv.get(k, 0) + 1
    lines = [
        f"# Daily Report {today} (ET)",
        "",
        f"- signals today: {len(sig_today)}  breakdown: {json.dumps(conv, ensure_ascii=False)}",
        f"- opens today: {len(exec_today)}   closes today: {len(closed_today)}",
        f"- open positions: {len(pos)} -> {', '.join(pos) if pos else '-'}",
        "",
        "## Cumulative (H1 forward, paper $100k)",
        "```json",
        json.dumps(s, indent=1),
        "```",
        "",
        "## Closed today",
    ]
    for t in closed_today:
        lines.append(f"- {t['ticker']}: {t['exit_reason']} pnl ${t['pnl']} ({t['ret_net']*1e4:.0f}bps) thesis: {t['signal'].get('thesis','')[:90]}")
    if not closed_today:
        lines.append("- none")
    out = ROOT / "reports" / f"daily_{today}.md"
    out.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\n[saved {out}]")


if __name__ == "__main__":
    main()
