"""SEC EDGAR 层：full-text search API 扫 8-K，Archives 拉全文。合规 UA，限速 <2 req/s。"""
import json
import re
import time
from html import unescape
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FILINGS = DATA / "filings"
FILINGS.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "alphatrade personal research ralph.wen@gmail.com"}
_last_req = [0.0]


def _get(url, params=None, timeout=20):
    dt = time.time() - _last_req[0]
    if dt < 0.55:
        time.sleep(0.55 - dt)
    r = requests.get(url, params=params, headers=UA, timeout=timeout)
    _last_req[0] = time.time()
    r.raise_for_status()
    return r


def search_8k(startdt: str, enddt: str, max_pages=40):
    """EDGAR full-text search：返回窗口内全部 8-K 元数据 hits（含 items、display_names）。
    日期格式 YYYY-MM-DD（file_date 粒度是天，盘中增量靠 seen 去重）。"""
    out = []
    for page in range(max_pages):
        params = {
            "q": "\"\"",
            "forms": "8-K",
            "startdt": startdt,
            "enddt": enddt,
            "from": page * 100,
        }
        try:
            j = _get("https://efts.sec.gov/LATEST/search-index", params=params).json()
        except Exception:  # noqa: BLE001
            if page == 0:
                raise
            break
        hits = j.get("hits", {}).get("hits", [])
        out.extend(h.get("_source", {}) | {"_id": h.get("_id", "")} for h in hits)
        total = j.get("hits", {}).get("total", {}).get("value", 0)
        if (page + 1) * 100 >= min(total, max_pages * 100) or not hits:
            break
    return out


_TICKER_RE = re.compile(r"\(([A-Z][A-Z0-9.\-]{0,9})\)\s+\(CIK")


def parse_hit(src: dict):
    """从 efts hit 提取 (adsh, cik, ticker, name, items, accepted)。ticker 可能为 None。"""
    adsh = src.get("adsh") or (src.get("_id", "").split(":")[0])
    ciks = src.get("ciks") or []
    names = src.get("display_names") or []
    ticker = None
    name = names[0] if names else ""
    m = _TICKER_RE.search(name)
    if m:
        ticker = m.group(1)
    items = src.get("items") or []
    if isinstance(items, str):
        items = [x.strip() for x in items.split(",") if x.strip()]
    return {
        "adsh": adsh,
        "cik": ciks[0].lstrip("0") if ciks else None,
        "ticker": ticker,
        "company": re.sub(r"\s*\([^)]*\)\s*$", "", re.sub(r"\s*\(CIK[^)]*\)\s*$", "", name)).strip(),
        "items": items,
        "file_date": src.get("file_date"),
        "accepted": src.get("file_date_accepted") or src.get("accepted") or "",
    }


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t\r\f\v]+")


def _strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?i)<(br|/p|/div|/tr|/li|/h[1-6])[^>]*>", "\n", html)
    text = unescape(_TAG_RE.sub(" ", html))
    text = _WS_RE.sub(" ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def fetch_filing_text(cik: str, adsh: str, max_chars=18000) -> dict:
    """拉主文档 + press release exhibit (EX-99*) 文本。缓存到 data/filings/。"""
    key = adsh.replace("-", "")
    cache = FILINGS / f"{key}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    idx = _get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{key}/index.json").json()
    files = [f["name"] for f in idx.get("directory", {}).get("item", [])]
    htmls = [f for f in files if f.lower().endswith((".htm", ".html")) and "index" not in f.lower()]
    # 主文档：8-K 本体通常含 '8k'/'8-k' 或是第一个 htm；exhibits 含 ex99/ex-99
    main = sorted(htmls, key=lambda f: (("8k" not in f.lower().replace("-", "")), len(f)))[:1]
    exhibits = [f for f in htmls if re.search(r"ex[-_]?99", f.lower())][:2]
    parts = []
    for fn in dict.fromkeys(main + exhibits):
        try:
            raw = _get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{key}/{fn}").text
            parts.append(f"===== {fn} =====\n{_strip_html(raw)}")
        except Exception as e:  # noqa: BLE001
            parts.append(f"===== {fn} FETCH-ERROR {e} =====")
    text = "\n\n".join(parts)[:max_chars]
    doc = {"cik": cik, "adsh": adsh, "files": files, "text": text}
    cache.write_text(json.dumps(doc))
    return doc


if __name__ == "__main__":
    import sys
    d1, d2 = sys.argv[1], sys.argv[2]
    hits = search_8k(d1, d2)
    print(f"8-K filings {d1}..{d2}: {len(hits)}")
    for h in hits[:5]:
        print(json.dumps(parse_hit(h), ensure_ascii=False))
