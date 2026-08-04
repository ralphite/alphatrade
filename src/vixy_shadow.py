"""H14 影子运行(不动钱)。用户裁决 2026-08-03:先影子 3 个月再决定是否上线。

规则(预注册,冻结,与 research_h14.py 完全一致):
  昨收 ^VIX >= ^VIX3M(倒挂) -> 今日在场持 VIXY;否则空仓。成本 10bps/边,仅在状态切换日计。
记录:每日信号 + 假设 sleeve($5k 名义)净值 + 同日 QQQ 收益(用于事后算相关性/对冲赔付)。
状态:ledger/vixy_shadow.json;流水:ledger/vixy_shadow_daily.jsonl
复审日:2026-11-03(3 个月)。判据见 HYPOTHESES.md H14-S。
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yfinance as yf

sys.path.insert(0, str(Path(__file__).parent))
from ledger import log_event  # noqa: E402

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "ledger" / "vixy_shadow.json"
DAILY = ROOT / "ledger" / "vixy_shadow_daily.jsonl"
NOTIONAL = 5_000.0
COST_BPS = 10.0
REVIEW = "2026-11-03"


def closes(sym, n=5):
    # 注意:^VIX3M 用 period="5d" 只返回 1 根(yfinance 对该指数的已知怪癖),必须取更长窗口
    h = yf.Ticker(sym).history(period="1mo")["Close"].dropna()
    return [float(x) for x in h][-n:], [d.strftime("%Y-%m-%d") for d in h.index][-n:]


def main():
    today = datetime.now(ET).strftime("%Y-%m-%d")
    vix, dv = closes("^VIX")
    v3m, _ = closes("^VIX3M")
    vixy, dvx = closes("VIXY")

    # 信号用「昨收」:今日收盘轮里,最新一根就是今天,故取倒数第二根做昨收
    if len(vix) < 2 or len(v3m) < 2 or len(vixy) < 2:
        print("[H14-S] 数据不足,跳过")
        return
    prev_vix, prev_v3m = vix[-2], v3m[-2]
    in_pos = prev_vix >= prev_v3m  # 今日是否应在场

    st = json.loads(STATE.read_text()) if STATE.exists() else {
        "inception": today, "notional": NOTIONAL, "value": NOTIONAL,
        "in_pos": False, "review": REVIEW, "days": 0, "days_in": 0}
    if st.get("last_date") == today:
        print(f"[H14-S] {today} 已记录,跳过")
        return

    # 今日 sleeve 收益:昨日是否在场决定今日是否吃 VIXY 日收益(严格无 lookahead:
    # 状态在昨收就已确定,今日全天在场)
    vixy_ret = vixy[-1] / vixy[-2] - 1
    ret = vixy_ret if in_pos else 0.0
    if in_pos != st["in_pos"]:
        ret -= COST_BPS / 1e4  # 切换日一次成本
    st["value"] = round(st["value"] * (1 + ret), 2)
    st["in_pos"], st["last_date"] = in_pos, today
    st["days"] += 1
    st["days_in"] += 1 if in_pos else 0

    qh, _ = closes("QQQ")
    qqq_ret = qh[-1] / qh[-2] - 1

    rec = {"date": today, "in_pos": in_pos, "vix_prev": round(prev_vix, 2), "v3m_prev": round(prev_v3m, 2),
           "vixy_ret_bps": round(vixy_ret * 1e4, 1), "sleeve_ret_bps": round(ret * 1e4, 1),
           "qqq_ret_bps": round(qqq_ret * 1e4, 1), "value": st["value"]}
    with DAILY.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    STATE.write_text(json.dumps(st, indent=1))
    log_event("vixy_shadow", rec)

    pnl = (st["value"] / NOTIONAL - 1) * 1e4
    print(f"[H14-S] {today} {'在场' if in_pos else '空仓'} (VIX {prev_vix:.1f}/{prev_v3m:.1f}) "
          f"日 {ret*1e4:+.0f}bps | 影子净值 ${st['value']:,.0f} ({pnl:+.0f}bps) | "
          f"{st['days_in']}/{st['days']}d 在场 | 复审 {REVIEW}")


if __name__ == "__main__":
    main()
