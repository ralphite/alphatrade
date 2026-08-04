"""H13 关卡 1:国债拍卖周期(7y/10y Note 拍卖 -> IEF)。预注册判据见 HYPOTHESES.md。

形态 A:拍卖日收盘买入 IEF,持有 3 个交易日收盘卖出。
形态 B(机制对照):拍卖日前 3 个交易日收盘买入,拍卖日收盘卖出(机制成立则为负)。
成本 2bps/边。
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "treasury_auctions.json"
UA = {"User-Agent": "alphatrade-research ralph.wen@gmail.com"}
COST_BPS = 2.0
HOLD = 3
SEGMENTS = [("2007-2012", "2007-01-01", "2012-12-31"),
            ("2013-2019", "2013-01-01", "2019-12-31"),
            ("2020-2026", "2020-01-01", "2026-12-31")]


def fetch_auctions():
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    out = []
    url = "https://www.treasurydirect.gov/TA_WS/securities/search"
    for term in ["7-Year", "10-Year"]:
        page = 0
        while True:
            r = requests.get(url, params={"format": "json", "type": "Note", "securityTerm": term,
                                          "pagesize": 250, "pagenum": page}, headers=UA, timeout=30)
            r.raise_for_status()
            js = r.json()
            if not js:
                break
            out += [{"term": term, "auctionDate": x["auctionDate"][:10], "cusip": x["cusip"],
                     "offering": x.get("offeringAmount"), "reopening": x.get("reopening")} for x in js]
            if len(js) < 250:
                break
            page += 1
    CACHE.write_text(json.dumps(out, indent=1))
    return out


def tstat(x):
    x = np.asarray(x, float)
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 and x.std() > 0 else float("nan")


def pval(t):
    return 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if t == t else float("nan")


def main():
    auc = fetch_auctions()
    dates = sorted({a["auctionDate"] for a in auc if a["auctionDate"] >= "2006-01-01"})
    print(f"拍卖事件:{len(auc)} 条(7y+10y,含 reopening) → 去重拍卖日 {len(dates)} 个 "
          f"({dates[0]} .. {dates[-1]})")

    h = yf.Ticker("IEF").history(start="2006-06-01", end="2026-08-04", auto_adjust=True)["Close"]
    h.index = pd.to_datetime([d.strftime("%Y-%m-%d") for d in h.index])
    px = h.sort_index()
    idx = list(px.index)
    pos = {d: i for i, d in enumerate(idx)}
    ret = px.pct_change()

    # 月末最后 4 个交易日(H9 窗口)标记,用于去重
    ym = pd.Series(px.index, index=px.index).dt.to_period("M")
    h9_days = set()
    for _, grp in pd.Series(px.index, index=px.index).groupby(ym):
        h9_days.update(list(grp)[-4:])

    rows = []
    for d in dates:
        ts = pd.Timestamp(d)
        # 拍卖日若非交易日,取其后第一个交易日
        if ts not in pos:
            later = [x for x in idx if x > ts]
            if not later:
                continue
            ts = later[0]
        i = pos[ts]
        if i - HOLD < 0 or i + HOLD >= len(idx):
            continue
        pa, pb = px.iloc[i], px.iloc[i + HOLD]
        pre = px.iloc[i - HOLD]
        rows.append({
            "date": ts, "i": i,
            "A_ret": (pb / pa - 1) - 2 * COST_BPS / 1e4,     # 拍卖日 -> +3d
            "B_ret": (pa / pre - 1) - 2 * COST_BPS / 1e4,    # -3d -> 拍卖日
            "A_daily": [ret.iloc[i + k] for k in range(1, HOLD + 1)],
            "in_h9": any(idx[i + k] in h9_days for k in range(1, HOLD + 1)),
        })
    ev = pd.DataFrame(rows)
    print(f"可用事件 {len(ev)} 个 | 与 H9 月末窗口重叠 {int(ev['in_h9'].sum())} 个 "
          f"({ev['in_h9'].mean()*100:.0f}%)")

    base_d = ret.dropna()
    base_mu = base_d.mean()
    print(f"\nIEF 全样本日均 {base_mu*1e4:+.2f}bps (n={len(base_d)}), {HOLD}日基准 {base_mu*HOLD*1e4:+.1f}bps")

    def report(tag, sub):
        if len(sub) < 5:
            print(f"  {tag}: 样本不足 (n={len(sub)})")
            return
        daily = np.array([r for lst in sub["A_daily"] for r in lst], float)
        diff_d = daily.mean() - base_mu
        t = tstat(daily - base_mu)
        a = sub["A_ret"].values
        print(f"  {tag:26s} n={len(sub):4d} | A净 {a.mean()*1e4:+7.1f}bps t={tstat(a):+5.2f} | "
              f"窗内日均 {daily.mean()*1e4:+6.2f}bps | 池内差分 {diff_d*1e4:+6.2f}bps/日 "
              f"t={t:+5.2f} (p={pval(t):.3f})")

    print("\n[判据1+3 形态 A:拍卖日收盘买入,持有 3 日]")
    report("全样本", ev)
    print("\n[判据3 三段分解]")
    for name, a, b in SEGMENTS:
        report(name, ev[(ev["date"] >= a) & (ev["date"] <= b)])

    print("\n[判据4 与 H9 去重]")
    report("剔除月末窗口重叠", ev[~ev["in_h9"]])
    report("仅月末窗口重叠", ev[ev["in_h9"]])

    print("\n[判据5 机制对照:形态 B(拍卖前 3 日)]")
    b = ev["B_ret"].values
    print(f"  B净 {b.mean()*1e4:+.1f}bps t={tstat(b):+.2f} (机制成立应为负) | "
          f"3日基准 {base_mu*HOLD*1e4:+.1f}bps | 差分 {(b.mean()-base_mu*HOLD)*1e4:+.1f}bps")

    print("\n[判据3 单位在场时间]")
    inmkt_days = len(ev) * HOLD
    print(f"  在场 {inmkt_days} 日 / 全样本 {len(base_d)} 日 = {inmkt_days/len(base_d)*100:.1f}% 时间")
    tot = np.prod(1 + ev["A_ret"].values) - 1
    yrs = (ev['date'].iloc[-1] - ev['date'].iloc[0]).days / 365.25
    bh = (px.iloc[-1] / px.loc[ev['date'].iloc[0]]) - 1
    print(f"  策略累计 {tot*100:+.1f}% ({yrs:.1f}年,年化 {((1+tot)**(1/yrs)-1)*100:+.2f}%) | "
          f"IEF 买入持有同期 {bh*100:+.1f}% (年化 {((1+bh)**(1/yrs)-1)*100:+.2f}%)")

    print("\n[稳健性:按持有期扫描(仅供机制形状参考,不作为判据)]")
    for hold in [1, 2, 3, 5, 10]:
        rr = []
        for _, r in ev.iterrows():
            i = int(r["i"])
            if i + hold < len(idx):
                rr.append((px.iloc[i + hold] / px.iloc[i] - 1) - 2 * COST_BPS / 1e4)
        rr = np.array(rr)
        print(f"  hold={hold:2d}d: 净 {rr.mean()*1e4:+6.1f}bps t={tstat(rr):+5.2f} | "
              f"基准 {base_mu*hold*1e4:+6.1f}bps | 差分 {(rr.mean()-base_mu*hold)*1e4:+6.1f}bps")


if __name__ == "__main__":
    sys.exit(main())
