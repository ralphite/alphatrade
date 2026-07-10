"""Gemini 第二意见：用相同的 eval_8k_v1 指令让 Gemini 独立评估同一批 filing，量化跨模型一致率。

用途（研究，不改主流程）：
  1. 一致率低 → LLM 评估的"信号"可能主要是模型噪声 → H1 前提存疑
  2. 一致率高但双方都无区分力 → 事件本身没有信息
  3. red-team 关的跨家族反驳者候选

用法：.venv/bin/python src/gemini_review.py <queue.json> <signals.jsonl> <out.jsonl>
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = "gemini-pro-latest"


def api_key():
    for line in (ROOT.parent / "agentrunner" / ".env").read_text().splitlines():
        if line.startswith("GEMINI_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("no GEMINI_API_KEY")


def eval_instructions():
    return (ROOT / "prompts" / "eval_8k_v1.md").read_text()


def call_gemini(prompt: str, tries=3) -> str:
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8000,
                             "responseMimeType": "application/json"},
    }).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key()}"
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                j = json.loads(r.read())
            return j["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))
    return ""


def second_opinion(filing: dict) -> dict:
    instr = eval_instructions()
    meta = {k: filing.get(k) for k in ("ticker", "company", "market_cap", "items", "file_date",
                                       "accepted", "prev_close", "chg_since_event_pct", "adv_dollars")}
    prompt = f"""{instr}

---
今天是 {filing.get('file_date')} 之后的下一个美股交易日盘前。你按上述指令独立评估以下 8-K。
注意：accepted 字段为 UTC 时间（减 4 小时 = 美东）。chg_since_event_pct 为 None 时表示无价格数据可用，priced_in_check 需明确说明是在无价格数据下的推断。
只输出一个 JSON 对象，不要其他文字。

元数据：{json.dumps(meta, ensure_ascii=False)}

8-K 全文：
{filing.get('text','')[:15000]}
"""
    raw = call_gemini(prompt)
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return {"ticker": filing["ticker"], "error": "no-json", "raw": raw[:300]}
    try:
        out = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return {"ticker": filing["ticker"], "error": "bad-json", "raw": raw[:300]}
    out["signal_id"] = filing.get("signal_id")
    out["second_model"] = MODEL
    return out


def main(queue_path, signals_path, out_path):
    queue = {x["signal_id"]: x for x in json.loads(Path(queue_path).read_text())}
    sigs = [json.loads(x) for x in Path(signals_path).read_text().splitlines() if x.strip()]
    rows = []
    agree_dir = agree_conv = both = 0
    for s in sigs:
        f = queue.get(s["signal_id"])
        if not f:
            continue
        g = second_opinion(f)
        row = {"signal_id": s["signal_id"], "ticker": s["ticker"],
               "claude": {"direction": s.get("direction"), "conviction": s.get("conviction")},
               "gemini": {"direction": g.get("direction"), "conviction": g.get("conviction"),
                          "thesis": g.get("thesis"), "error": g.get("error")}}
        rows.append(row)
        if not g.get("error"):
            both += 1
            if g.get("direction") == s.get("direction"):
                agree_dir += 1
                if g.get("conviction") == s.get("conviction"):
                    agree_conv += 1
        print(f"{s['ticker']:6s} C:{s.get('direction')}/{s.get('conviction')} G:{g.get('direction')}/{g.get('conviction')} {('ERR:'+str(g.get('error'))) if g.get('error') else ''}")
        time.sleep(1.0)
    Path(out_path).write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
    if both:
        print(f"\nagreement: direction {agree_dir}/{both} ({agree_dir/both:.0%}), direction+conviction {agree_conv}/{both} ({agree_conv/both:.0%})")


if __name__ == "__main__":
    main(*sys.argv[1:4])
