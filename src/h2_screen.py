"""H2 预检：从 defeatbeta 拉取窗口内财报 transcript，生成评估队列。

用 python3.11 venv 运行：.venv311/bin/python src/h2_screen.py 2026-03-01 2026-05-31 100
（universe = 5 个历史窗口 queue 的全部 ticker，已过流动性 gate）
输出：research/h2_screen/batch_*.json（每条含 transcript 全文，截 22k chars）
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "h2_screen"
OUT.mkdir(parents=True, exist_ok=True)


def universe():
    seen = set()
    for q in ROOT.glob("research/screen_*/queue.json"):
        for x in json.loads(q.read_text()):
            seen.add(x["ticker"])
    return sorted(seen)


def main(start, end, max_n):
    from defeatbeta_api.data.ticker import Ticker
    tickers = universe()
    print(f"universe {len(tickers)} tickers; window {start}..{end}; target {max_n}")
    rows, fails = [], 0
    for i, t in enumerate(tickers):
        if len(rows) >= max_n:
            break
        try:
            tk = Ticker(t)
            lst = tk.earning_call_transcripts().get_transcripts_list()
            hit = lst[(lst["report_date"] >= start) & (lst["report_date"] <= end)]
            for _, r in hit.iterrows():
                if len(rows) >= max_n:
                    break
                tr = tk.earning_call_transcripts().get_transcript(int(r["fiscal_year"]), int(r["fiscal_quarter"]))
                # transcript 为 DataFrame(paragraph 行) 或对象；拼成文本
                if hasattr(tr, "iterrows"):
                    text = "\n".join(f"{row.get('speaker','')}: {row.get('content','')}"
                                     for _, row in tr.iterrows())
                else:
                    text = str(tr)
                if len(text) < 3000:
                    continue
                rows.append({
                    "signal_id": f"{t}_{r['fiscal_year']}Q{r['fiscal_quarter']}",
                    "ticker": t, "fiscal": f"{r['fiscal_year']}Q{r['fiscal_quarter']}",
                    "report_date": str(r["report_date"]),
                    "text": text[:22000],
                })
        except Exception:  # noqa: BLE001
            fails += 1
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(tickers)} scanned, {len(rows)} collected, {fails} fails", flush=True)
    n_batch = max(1, (len(rows) + 8) // 9)
    for b in range(n_batch):
        (OUT / f"batch_{b}.json").write_text(json.dumps(rows[b::n_batch], ensure_ascii=False, indent=1))
    print(json.dumps({"collected": len(rows), "fails": fails, "batches": n_batch, "dir": str(OUT)}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 100)
