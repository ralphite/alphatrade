"""Form 345（内部人交易）结构化数据管线：SEC 季度 zip → 内部人买入表 → 集群事件表。

三段式：
  download  拉 https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/
            的季度 zip 到 data/form345/zip/（合规 UA + 限速，已存在则跳过）
  buys      逐季度解压 SUBMISSION / NONDERIV_TRANS / REPORTINGOWNER（+ FOOTNOTES 只做 10b5-1
            文本探测），过滤出「公开市场买入」，跨季度合并去重 → data/insider_buys.parquet
  clusters  在买入表上做集群检测（同一发行人 / 滚动 7 日历日 / ≥2 个不同内部人 / 合计 ≥$250k）
            → data/insider_clusters.csv

只产事件表，不做回测（回测由主 agent 按池内差分纪律做）。

设计上踩过的坑（改动前先读）：
1. **一张 Form 4 可以有多个 reporting owner**（基金系 GP/LP/个人联合申报，实测 P 类申报里 ~8%）。
   若按 RPTOWNERCIK 数「不同内部人」，一张 10 人联合申报单会被误判成 10 人集群。
   → 交易行不按 owner 展开（否则金额也翻倍）；集群里的「不同内部人」用**并查集**：
     任意两张申报单只要共享一个 owner CIK 就并成同一个内部人实体。
2. **10% 股东（PE/VC）不是高管信念信号**。不剔除，但单列 is_tenpercent / n_insiders_exec，
   让回测端自行收紧。
3. **AFF10B5ONE（10b5-1 计划标志）2023 年才进表**（SEC 2022-12 加的封面勾选框）。
   早年季度该列不存在 → 只能按年报告覆盖率；另外用 FOOTNOTES 文本兜底给 flag（不删行）。
4. **申报日 ≠ 信号可得日**。集群的 last_filing_date 是最后一笔的申报日；但一个 3 人集群
   可能在第 2 个人申报时就已经满足门槛。signal_date = 按申报日逐日回放、**首次**出现
   「7 日交易窗内 ≥2 内部人且 ≥$250k」的那一天 = 真正无前视的建仓可得时点。回测用 signal_date。
5. **发行人主键用 ISSUERCIK 不用 ticker**（换名/退市/ticker 复用 → 生存偏差）。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
F345 = DATA / "form345"
ZIPDIR = F345 / "zip"
TMPDIR = F345 / "_tmp"
BUYS_PARQUET = DATA / "insider_buys.parquet"
BUYS_CSV = DATA / "insider_buys.csv.gz"
CLUSTERS_CSV = DATA / "insider_clusters.csv"

UA = {"User-Agent": "alphatrade research ralph.wen@gmail.com"}
URL = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{q}_form345.zip"

# 2015Q4 是**热身季度**：集群要求 ≥2 个内部人，若第一个人在 2015-12 申报、第二个在 2016-01 申报，
# 不拉热身季就会漏掉 2016 年初的事件。热身季自身的事件不完整 → 集群表按 USABLE_FROM 截断。
START_YEAR, START_Q = 2015, 4
USABLE_FROM = pd.Timestamp("2016-01-01")
WINDOW_DAYS = 7          # 集群窗口：末笔 - 首笔 <= 7 个日历日
MIN_INSIDERS = 2         # 不同内部人实体数（并查集后）
MIN_VALUE = 250_000.0    # 合计金额 USD

SUB_COLS = ["ACCESSION_NUMBER", "FILING_DATE", "PERIOD_OF_REPORT", "DOCUMENT_TYPE",
            "ISSUERCIK", "ISSUERNAME", "ISSUERTRADINGSYMBOL", "AFF10B5ONE"]
ND_COLS = ["ACCESSION_NUMBER", "SECURITY_TITLE", "TRANS_DATE", "TRANS_CODE", "TRANS_SHARES",
           "TRANS_PRICEPERSHARE", "TRANS_ACQUIRED_DISP_CD", "DIRECT_INDIRECT_OWNERSHIP",
           "TRANS_TIMELINESS"]
RO_COLS = ["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNERNAME", "RPTOWNER_RELATIONSHIP",
           "RPTOWNER_TITLE", "RPTOWNER_TXT"]

_TRUE = {"1", "true", "TRUE", "True", "Y", "y"}
_BAD_TICKER = {"", "NONE", "N/A", "NA", "N.A.", "NONE.", "NULL", "N/A.", "NOT APPLICABLE",
               "PRIVATE", "0", "-", "--", "[NONE]"}
_EXCH_RE = re.compile(r"^(NYSE\s*MKT|NYSE\s*AMERICAN|NYSE|NASDAQ|AMEX|OTCBB|OTCQB|OTCQX|OTC|"
                      r"ASX|TSX|CBOE|BATS)\s*[:\-]\s*", re.I)
_TICKER_OK = re.compile(r"^[A-Z][A-Z0-9]{0,5}([.\-][A-Z]{1,2})?$")
# 单笔价格上限：全样本最贵的真实标的是 BRK.A（~$408k/股）。超过 $1M/股一律是申报人把
# 总金额填进了单价栏（实测 KYN/NTG/TYG/DNP 等封闭式基金填成 $5,000,000）。
MAX_PRICE = 1_000_000.0
_CEO_RE = re.compile(r"\bC\.?E\.?O\.?\b|chief\s+exec", re.I)
_CFO_RE = re.compile(r"\bC\.?F\.?O\.?\b|chief\s+financ", re.I)
_10B5_RE = re.compile(r"10b5[\s\-–]?1", re.I)


# ---------------------------------------------------------------- download

def quarters(start=(START_YEAR, START_Q), end=None):
    y, q = start
    if end is None:
        today = pd.Timestamp.today()
        end = (today.year, (today.month - 1) // 3 + 1)
    out = []
    while (y, q) <= end:
        out.append(f"{y}q{q}")
        q += 1
        if q == 5:
            y, q = y + 1, 1
    return out


def download(force=False, sleep=0.4):
    """拉季度 zip。未发布的季度返回 404 → 停在最后一个可得季度。"""
    ZIPDIR.mkdir(parents=True, exist_ok=True)
    got, skipped, missing = [], [], []
    for q in quarters():
        dest = ZIPDIR / f"{q}_form345.zip"
        if dest.exists() and dest.stat().st_size > 1_000_000 and not force:
            skipped.append(q)
            continue
        time.sleep(sleep)
        r = requests.get(URL.format(q=q), headers=UA, timeout=180)
        if r.status_code == 404:
            missing.append(q)
            print(f"  {q}: 404（尚未发布）")
            continue
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"  {q}: {len(r.content)/1e6:.1f} MB")
        got.append(q)
    print(f"download: 新增 {len(got)}，已有 {len(skipped)}，未发布 {len(missing)}")
    return sorted(p.name[:6] for p in ZIPDIR.glob("*_form345.zip"))


# ---------------------------------------------------------------- parse

def _read_tsv(path: Path, cols):
    """SEC 的 TSV 里 REMARKS/FOOTNOTE 会带裸引号 → quoting=3（QUOTE_NONE）。缺列容忍。"""
    head = pd.read_csv(path, sep="\t", nrows=0, quoting=3)
    use = [c for c in cols if c in head.columns]
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, quoting=3,
                     usecols=use, on_bad_lines="skip", engine="c")
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


def _dates(s):
    return pd.to_datetime(s.str.strip(), format="%d-%b-%Y", errors="coerce")


def clean_ticker(raw: str) -> str:
    """ISSUERTRADINGSYMBOL 是申报人手填的自由文本，实测垃圾形态：交易所前缀（`NYSE:FBC`）、
    引号/括号包裹（`\"\"\"TARA\"\"\"`、`(CALX)`、`?OSH?`）、双重股权并列（`ISCA, ISCB`、
    `HEI, HEI.A`）。这里只做保守清洗，判不了的返回 ""，再由 _fix_tickers() 用同一发行人
    其他申报里的正常 ticker 回填（比直接猜第一个 token 安全）。"""
    t = _EXCH_RE.sub("", str(raw).strip().upper())
    t = re.sub(r"^[^A-Z0-9]+|[^A-Z0-9]+$", "", t)      # 剥掉首尾的引号/括号/问号
    if not t or t in _BAD_TICKER:
        return ""
    if re.search(r"[\s,;/:]", t):                       # 多 ticker 并列或残留交易所后缀 → 交给回填
        return ""
    return t if _TICKER_OK.match(t) else ""


def _first_token(raw: str) -> str:
    """并列写法（双重股权/带交易所后缀）取第一个 token：`ISCA, ISCB`→ISCA、`HEI, HEI.A`→HEI、
    `AROC US`→AROC、`PAYD:OTC`→PAYD。单字母 token（`N O G`、`Z AND ZG`）一律拒绝——
    猜错会映射到别家公司的真实 ticker，比丢掉这行危险得多。"""
    t = _EXCH_RE.sub("", str(raw).strip().upper())
    tok = re.split(r"[\s,;/:]+", re.sub(r"^[^A-Z0-9]+", "", t))
    tok = [x for x in tok if x]
    if not tok:
        return ""
    first = re.sub(r"[^A-Z0-9.\-]+$", "", tok[0])
    if len(first) < 2 or first in _BAD_TICKER:
        return ""
    return first if _TICKER_OK.match(first) else ""


def _fix_tickers(buys: pd.DataFrame) -> pd.DataFrame:
    """三级回收，越靠后越不可信：
    1) clean_ticker 保守清洗；
    2) 同 issuer_cik 众数回填（该发行人别的申报里填对过 → 最可靠）；
    3) 并列写法取第一个 token（ISCA/HEI 这类发行人**每次**都写成并列，众数救不了）。"""
    raw = buys.ticker.copy()
    buys["ticker"] = raw.map(clean_ticker)
    ok = buys[buys.ticker != ""]
    mode = ok.groupby("issuer_cik").ticker.agg(lambda s: s.value_counts().idxmax())
    miss = buys.ticker == ""
    buys.loc[miss, "ticker"] = buys.loc[miss, "issuer_cik"].map(mode).fillna("")
    miss = buys.ticker == ""
    buys.loc[miss, "ticker"] = raw[miss].map(_first_token)
    return buys


def parse_quarter(qtr: str, keep_footnotes=True) -> pd.DataFrame:
    """解压 → 过滤 code P 买入 → 拼 SUBMISSION / REPORTINGOWNER → 每行一笔买入。用完删中间文件。"""
    zpath = ZIPDIR / f"{qtr}_form345.zip"
    tmp = TMPDIR / qtr
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    try:
        with zipfile.ZipFile(zpath) as z:
            names = set(z.namelist())
            want = ["SUBMISSION.tsv", "NONDERIV_TRANS.tsv", "REPORTINGOWNER.tsv"]
            if keep_footnotes and "FOOTNOTES.tsv" in names:
                want.append("FOOTNOTES.tsv")
            for n in want:
                z.extract(n, tmp)

        nd = _read_tsv(tmp / "NONDERIV_TRANS.tsv", ND_COLS)
        nd = nd[(nd.TRANS_CODE.str.strip() == "P") &
                (nd.TRANS_ACQUIRED_DISP_CD.str.strip() == "A")].copy()
        if nd.empty:
            return pd.DataFrame()

        sub = _read_tsv(tmp / "SUBMISSION.tsv", SUB_COLS)
        sub = sub[sub.DOCUMENT_TYPE.str.strip().isin(["4", "4/A"])].copy()
        df = nd.merge(sub, on="ACCESSION_NUMBER", how="inner")
        if df.empty:
            return pd.DataFrame()

        # 一张申报单多个 owner → 折叠成一行，不展开（展开会把金额和内部人数都灌水）
        ro = _read_tsv(tmp / "REPORTINGOWNER.tsv", RO_COLS)
        ro = ro[ro.ACCESSION_NUMBER.isin(set(df.ACCESSION_NUMBER))].copy()
        ro["RPTOWNERCIK"] = ro.RPTOWNERCIK.str.strip().str.lstrip("0")
        rel = ro.RPTOWNER_RELATIONSHIP.fillna("")
        ro["_dir"] = rel.str.contains("Director", case=False)
        ro["_off"] = rel.str.contains("Officer", case=False)
        ro["_ten"] = rel.str.contains("TenPercent", case=False)
        ro["_oth"] = rel.str.contains("Other", case=False)
        ro["_title"] = (ro.RPTOWNER_TITLE.fillna("") + " " + ro.RPTOWNER_TXT.fillna("")).str.strip()
        agg = ro.groupby("ACCESSION_NUMBER").agg(
            owner_ciks=("RPTOWNERCIK", lambda s: "|".join(sorted(set(x for x in s if x)))),
            owner_names=("RPTOWNERNAME", lambda s: "|".join(sorted(set(x.strip() for x in s if x.strip()))[:6])),
            n_filing_owners=("RPTOWNERCIK", "nunique"),
            is_director=("_dir", "any"), is_officer=("_off", "any"),
            is_tenpercent=("_ten", "any"), is_other=("_oth", "any"),
            owner_titles=("_title", lambda s: "; ".join(x for x in s if x)[:200]),
        ).reset_index()
        df = df.merge(agg, on="ACCESSION_NUMBER", how="left")

        # 10b5-1：AFF10B5ONE 是权威字段（2023 起才有）；FOOTNOTES 文本做早年兜底 flag
        fn_acc = set()
        fpath = tmp / "FOOTNOTES.tsv"
        if fpath.exists():
            fn = _read_tsv(fpath, ["ACCESSION_NUMBER", "FOOTNOTE_TXT"])
            fn = fn[fn.ACCESSION_NUMBER.isin(set(df.ACCESSION_NUMBER))]
            fn_acc = set(fn.loc[fn.FOOTNOTE_TXT.str.contains(_10B5_RE, na=False), "ACCESSION_NUMBER"])

        out = pd.DataFrame({
            "accession": df.ACCESSION_NUMBER,
            "issuer_cik": df.ISSUERCIK.str.strip().str.lstrip("0"),
            "issuer_name": df.ISSUERNAME.fillna("").str.strip(),
            "ticker": df.ISSUERTRADINGSYMBOL.str.strip().str.upper(),   # 清洗推迟到 concat 之后
            "doc_type": df.DOCUMENT_TYPE.str.strip(),
            "security_title": df.SECURITY_TITLE.str.strip(),
            "trans_date": _dates(df.TRANS_DATE),
            "filing_date": _dates(df.FILING_DATE),
            "shares": pd.to_numeric(df.TRANS_SHARES, errors="coerce"),
            "price": pd.to_numeric(df.TRANS_PRICEPERSHARE, errors="coerce"),
            "owner_ciks": df.owner_ciks.fillna(""),
            "owner_names": df.owner_names.fillna(""),
            "n_filing_owners": pd.to_numeric(df.n_filing_owners, errors="coerce").fillna(0).astype(int),
            "is_director": df.is_director.fillna(False).astype(bool),
            "is_officer": df.is_officer.fillna(False).astype(bool),
            "is_tenpercent": df.is_tenpercent.fillna(False).astype(bool),
            "is_other": df.is_other.fillna(False).astype(bool),
            "owner_titles": df.owner_titles.fillna(""),
            "direct_ownership": df.DIRECT_INDIRECT_OWNERSHIP.str.strip(),
            "aff10b5one_raw": df.AFF10B5ONE.str.strip(),
        })
        out["value_usd"] = out.shares * out.price
        out["is_ceo"] = out.owner_titles.str.contains(_CEO_RE, na=False)
        out["is_cfo"] = out.owner_titles.str.contains(_CFO_RE, na=False)
        out["flag_10b5_1"] = out.aff10b5one_raw.isin(_TRUE)
        out["flag_10b5_1_footnote"] = out.accession.isin(fn_acc)
        out["src_quarter"] = qtr
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build_buys(verbose=True) -> pd.DataFrame:
    zips = sorted(ZIPDIR.glob("*_form345.zip"))
    if not zips:
        sys.exit("data/form345/zip/ 是空的，先跑 download")
    frames, drop_log = [], []
    for z in zips:
        qtr = z.name[:6]
        df = parse_quarter(qtr)
        n0 = len(df)
        if n0:
            bad_price = (~(df.price > 0)) | (~(df.shares > 0)) | (df.price > MAX_PRICE)
            bad_date = df.trans_date.isna() | df.filing_date.isna()
            plan = df.flag_10b5_1
            keep = ~(bad_price | bad_date | plan)
            drop_log.append({"quarter": qtr, "raw_P": n0, "bad_price_or_shares": int(bad_price.sum()),
                             "bad_date": int(bad_date.sum()), "aff10b5one": int(plan.sum()),
                             "kept": int(keep.sum())})
            df = df[keep]
            frames.append(df)
        if verbose:
            print(f"  {qtr}: P买入 {n0} → 保留 {len(df) if n0 else 0}")
    buys = pd.concat(frames, ignore_index=True)

    # ticker 清洗 + 同发行人回填，必须在全量 concat 之后做（回填要跨季度找同一 issuer_cik）
    n_tkr = len(buys)
    buys = _fix_tickers(buys)
    buys = buys[buys.ticker != ""]
    print(f"ticker 清洗：丢弃无法归属的 {n_tkr - len(buys)} 行")

    # 交易日晚于申报日 = 数据错误（少量）
    bad = buys.trans_date > buys.filing_date
    buys = buys[~bad]

    # 4/A 修正单会把原始单的交易重报一遍 → 跨 accession 去重。
    # 注意：同一张 Form 4 内部出现两行完全一样的交易是**合法的**（同日不同账户/经纪商分笔，
    # 实测占重复行的 87%），不能一起 drop——否则金额被系统性低估。用 _occ 保留组内重数。
    key = ["issuer_cik", "owner_ciks", "security_title", "trans_date", "shares", "price",
           "direct_ownership"]
    n_pre = len(buys)
    buys["_occ"] = buys.groupby(key + ["accession"]).cumcount()
    buys = (buys.sort_values(["filing_date", "accession"])
                .drop_duplicates(subset=key + ["_occ"], keep="first")
                .drop(columns="_occ")
                .sort_values(["issuer_cik", "trans_date"])
                .reset_index(drop=True))
    buys["filing_lag_days"] = (buys.filing_date - buys.trans_date).dt.days
    print(f"\n合并：{n_pre} 行 → 去重后 {len(buys)} 行（丢弃 trans>filing {int(bad.sum())} 行，"
          f"重复/修正单 {n_pre - len(buys)} 行）")
    pd.DataFrame(drop_log).to_csv(F345 / "parse_log.csv", index=False)
    return buys


# ---------------------------------------------------------------- clusters

def _components(owner_sets):
    """并查集：共享任一 owner CIK 的申报单归为同一个内部人实体，返回实体数。"""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for s in owner_sets:
        for o in s:
            parent.setdefault(o, o)
        it = iter(s)
        first = next(it, None)
        for o in it:
            union(first, o)
    roots = {find(o) for s in owner_sets for o in s}
    return len(roots)


def _windows(d, v, sets, min_insiders, min_value, window):
    """d 已升序。逐笔当锚点，产出达标的 [lo, hi] 闭区间索引对。"""
    cum = np.concatenate([[0.0], np.cumsum(v)])
    ends = np.searchsorted(d, d + window, side="right")   # 每个锚点的窗口右开边界
    out = []
    for i in range(len(d)):
        hi = int(ends[i])
        if hi - i < min_insiders or cum[hi] - cum[i] < min_value:
            continue
        if _components(sets[i:hi]) >= min_insiders:
            out.append((i, hi - 1))
    return out


def _qualifies(sub, min_insiders, min_value, window):
    """sub 已按 trans_date 排序：内部是否存在一个 window 日窗满足门槛。"""
    return bool(_windows(sub["trans_date"].values, sub["value_usd"].values,
                         sub["_oset"].tolist(), min_insiders, min_value, window))


def detect_clusters(buys: pd.DataFrame, window_days=WINDOW_DAYS,
                    min_insiders=MIN_INSIDERS, min_value=MIN_VALUE) -> pd.DataFrame:
    win = pd.Timedelta(days=window_days).to_timedelta64()
    buys = buys.copy()
    buys["_oset"] = [frozenset(x.split("|")) if x else frozenset() for x in buys.owner_ciks]
    rows = []
    for cik, g in buys.groupby("issuer_cik", sort=False):
        if len(g) < min_insiders:
            continue
        g = g.sort_values(["trans_date", "filing_date"]).reset_index(drop=True)
        # 1) 锚定扫描：每笔交易作为窗口起点，判定该 7 日窗是否达标
        spans = _windows(g["trans_date"].values, g["value_usd"].values, g["_oset"].tolist(),
                         min_insiders, min_value, win)
        if not spans:
            continue
        # 2) 合并共享交易的达标窗口 → 一次连续买入行动 = 一个事件
        merged = [list(spans[0])]
        for lo, hi in spans[1:]:
            if lo <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])

        for lo, hi in merged:
            m = g.iloc[lo:hi + 1]
            # 3) signal_date：按申报日回放，首次出现「窗内达标」的日子（无前视）
            sig = None
            for fd in sorted(m.filing_date.unique()):
                pre = m[m.filing_date <= fd].sort_values("trans_date")
                if _qualifies(pre, min_insiders, min_value, win):
                    sig = pd.Timestamp(fd)
                    break
            if sig is None:                      # 兜底，理论上不会发生
                sig = pd.Timestamp(m.filing_date.max())
            # 主字段一律取 signal_date 当天可见的子集 pit（signal 之后才申报的买入不能进筛选口径，
            # 否则按 n_insiders / total_value 过滤就是前视）；全campaign 口径用 full_* 前缀，仅供描述。
            pit = m[m.filing_date <= sig]
            ex = pit[pit.is_director | pit.is_officer]
            rows.append({
                "ticker": pit.ticker.iloc[-1],
                "issuer_cik": cik,
                "issuer_name": pit.issuer_name.iloc[-1],
                "signal_date": sig.date(),
                "first_trans_date": pit.trans_date.min().date(),
                "last_trans_date": pit.trans_date.max().date(),
                "last_filing_date": m.filing_date.max().date(),   # 整段最后一笔的申报日
                "n_insiders": _components(pit._oset.tolist()),
                "n_insiders_exec": _components(ex._oset.tolist()) if len(ex) else 0,
                "n_trans": len(pit),
                "total_value_usd": round(float(pit.value_usd.sum()), 2),
                "value_exec_usd": round(float(ex.value_usd.sum()), 2),
                "total_shares": float(pit.shares.sum()),
                "avg_price": round(float(pit.value_usd.sum() / pit.shares.sum()), 4),
                # 单笔最大金额：SEC 数据里仍有申报人把总额填进股数栏的残余错误（价格栏已按
                # MAX_PRICE 拦掉），用它给回测端一个直接的离群过滤把手
                "max_trans_value_usd": round(float(pit.value_usd.max()), 2),
                "has_ceo": bool(pit.is_ceo.any()),
                "has_cfo": bool(pit.is_cfo.any()),
                "has_ceo_or_cfo": bool(pit.is_ceo.any() or pit.is_cfo.any()),
                "n_director_trans": int(pit.is_director.sum()),
                "n_officer_trans": int(pit.is_officer.sum()),
                "any_tenpercent": bool(pit.is_tenpercent.any()),
                "any_10b5_1_footnote": bool(pit.flag_10b5_1_footnote.any()),
                "trans_span_days": int((pit.trans_date.max() - pit.trans_date.min()).days),
                "owner_names": "|".join(sorted({x for s in pit.owner_names for x in s.split("|") if x}))[:200],
                # ---- 以下 full_* 是整段买入行动的事后口径，**不可用于建仓时的筛选** ----
                "full_n_insiders": _components(m._oset.tolist()),
                "full_n_trans": len(m),
                "full_total_value_usd": round(float(m.value_usd.sum()), 2),
                "full_last_trans_date": m.trans_date.max().date(),
                "full_trans_span_days": int((m.trans_date.max() - m.trans_date.min()).days),
            })
    cl = pd.DataFrame(rows)
    if cl.empty:
        return cl
    cl["signal_lag_days"] = (pd.to_datetime(cl.signal_date) - pd.to_datetime(cl.last_trans_date)).dt.days
    cl["filing_lag_days"] = (pd.to_datetime(cl.last_filing_date)
                             - pd.to_datetime(cl.full_last_trans_date)).dt.days
    cl["year"] = pd.to_datetime(cl.signal_date).dt.year
    cl = cl[pd.to_datetime(cl.signal_date) >= USABLE_FROM]     # 砍掉热身季度的不完整事件
    return cl.sort_values(["signal_date", "ticker"]).reset_index(drop=True)


# ---------------------------------------------------------------- stats

def print_stats(buys: pd.DataFrame, cl: pd.DataFrame):
    P = print
    P("\n" + "=" * 72)
    P("买入表 data/insider_buys")
    P("=" * 72)
    P(f"总买入笔数 {len(buys):,}｜发行人 {buys.issuer_cik.nunique():,}｜ticker {buys.ticker.nunique():,}"
      f"｜{buys.trans_date.min().date()} → {buys.trans_date.max().date()}")
    by = buys.assign(y=buys.trans_date.dt.year).groupby("y")
    P("\n每年买入笔数 / 金额中位数 / 10b5-1 字段覆盖率：")
    cov = buys.assign(y=buys.trans_date.dt.year).groupby("y").aff10b5one_raw.apply(lambda s: (s != "").mean())
    for y, n in by.size().items():
        P(f"  {y}  {n:7,}   中位 ${by.value_usd.median()[y]:>12,.0f}   AFF10B5ONE 非空 {cov[y]*100:5.1f}%")

    P("\n" + "=" * 72)
    P("集群事件表 data/insider_clusters.csv")
    P("=" * 72)
    P(f"总集群事件 {len(cl):,}｜不同 ticker {cl.ticker.nunique():,}"
      f"｜{cl.signal_date.min()} → {cl.signal_date.max()}")
    P(f"规则：同一 issuer_cik / 交易日滚动 {WINDOW_DAYS} 日历日 / ≥{MIN_INSIDERS} 个不同内部人实体 "
      f"/ 合计 ≥${MIN_VALUE:,.0f}")

    P("\n逐年集群事件数（按 signal_date 归年）：")
    g = cl.groupby("year")
    for y in sorted(cl.year.unique()):
        s = cl[cl.year == y]
        P(f"  {y}  {len(s):5,} 事件   {s.ticker.nunique():4,} ticker   "
          f"中位金额 ${s.total_value_usd.median():>10,.0f}   含CEO/CFO {s.has_ceo_or_cfo.mean()*100:4.1f}%   "
          f"≥3人 {(s.n_insiders >= 3).mean()*100:4.1f}%")

    P("\n每季度集群事件数：")
    qs = cl.assign(q=pd.to_datetime(cl.signal_date).dt.to_period("Q").astype(str)).groupby("q").size()
    P("  " + "  ".join(f"{k}:{v}" for k, v in qs.items()))

    P("\nticker 分布 top 20（出现次数最多的发行人）：")
    top = cl.groupby(["ticker", "issuer_name"]).size().sort_values(ascending=False).head(20)
    for (t, nm), n in top.items():
        P(f"  {t:<8} {n:4}  {nm[:52]}")
    P(f"\n单 ticker 事件数分布：1 次 {int((cl.groupby('ticker').size() == 1).sum()):,} 个 ticker，"
      f"中位 {cl.groupby('ticker').size().median():.0f}，最大 {cl.groupby('ticker').size().max()}")

    P("\n申报滞后（天）— 交易日 → 申报日：")
    for name, s in [("单笔买入 filing_date - trans_date", buys.filing_lag_days),
                    ("集群 last_filing_date - full_last_trans_date", cl.filing_lag_days),
                    ("集群 signal_date - last_trans_date（信号可得滞后）", cl.signal_lag_days),
                    ("集群 signal_date - first_trans_date", (pd.to_datetime(cl.signal_date) -
                                                             pd.to_datetime(cl.first_trans_date)).dt.days)]:
        P(f"  {name:<46} 中位 {s.median():5.0f}  P75 {s.quantile(.75):5.0f}  "
          f"P90 {s.quantile(.90):6.0f}  P99 {s.quantile(.99):7.0f}  max {s.max():7.0f}")
    P(f"\n  集群 signal_lag ≤2 天占比 {(cl.signal_lag_days <= 2).mean()*100:.1f}%，"
      f"≤5 天 {(cl.signal_lag_days <= 5).mean()*100:.1f}%，>45 天 {(cl.signal_lag_days > 45).mean()*100:.1f}%")
    P(f"  含 10% 股东的集群 {cl.any_tenpercent.mean()*100:.1f}%；"
      f"纯 director/officer 集群（n_insiders_exec≥2）{(cl.n_insiders_exec >= 2).mean()*100:.1f}%")
    P(f"  signal 后仍有后续买入的事件（full_n_trans > n_trans）{(cl.full_n_trans > cl.n_trans).mean()*100:.1f}%；"
      f"PIT 交易跨度 >{WINDOW_DAYS} 天 {(cl.trans_span_days > WINDOW_DAYS).mean()*100:.1f}%")


# ---------------------------------------------------------------- main

def load_buys():
    if BUYS_PARQUET.exists():
        return pd.read_parquet(BUYS_PARQUET)
    return pd.read_csv(BUYS_CSV, parse_dates=["trans_date", "filing_date"])


def save_buys(buys):
    cols = [c for c in buys.columns if not c.startswith("_")]
    try:
        buys[cols].to_parquet(BUYS_PARQUET, index=False)
        return BUYS_PARQUET
    except Exception as e:  # noqa: BLE001
        print(f"parquet 不可用（{e}），退回 csv.gz")
        buys[cols].to_csv(BUYS_CSV, index=False)
        return BUYS_CSV


def main():
    ap = argparse.ArgumentParser(description="Form 345 内部人集群买入数据管线")
    ap.add_argument("cmd", choices=["download", "buys", "clusters", "stats", "all"])
    ap.add_argument("--window", type=int, default=WINDOW_DAYS)
    ap.add_argument("--min-insiders", type=int, default=MIN_INSIDERS)
    ap.add_argument("--min-value", type=float, default=MIN_VALUE)
    a = ap.parse_args()
    F345.mkdir(parents=True, exist_ok=True)

    if a.cmd in ("download", "all"):
        print("[1/3] 下载 SEC Form 345 季度 zip")
        download()
    if a.cmd in ("buys", "all"):
        print("\n[2/3] 解析 → 内部人买入表")
        buys = build_buys()
        print(f"写出 {save_buys(buys)}")
    if a.cmd in ("clusters", "all", "stats"):
        buys = load_buys()
    if a.cmd in ("clusters", "all"):
        print("\n[3/3] 集群检测")
        cl = detect_clusters(buys, a.window, a.min_insiders, a.min_value)
        cl.to_csv(CLUSTERS_CSV, index=False)
        print(f"写出 {CLUSTERS_CSV}（{len(cl):,} 个集群事件）")
    if a.cmd in ("stats", "all"):
        cl = pd.read_csv(CLUSTERS_CSV)
        print_stats(buys, cl)


if __name__ == "__main__":
    main()
