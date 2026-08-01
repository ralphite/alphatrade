"""H6 AI 基建主题 sleeve 执行器(daily_close 调用)。
2026-08-01 门判定 PASS(5/5 发布 0 下调)+ 减半仲裁:$12.5k 上线(CRWV CDS 855bp 场外警讯),
8-14 Q2 13F 复核加满/退出。十标的权重按 research/h6_portfolio_draft.md 比例。
月度再平衡(暂缓至满仓决策后);每日仅 mark。
"""
import json, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0, str(Path(__file__).parent))
from data import fresh_price, daily_history
from ledger import log_event

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "ledger" / "h6_sleeve.json"
NOTIONAL = 12_500.0
SLIP = 15.0  # 中盘为主
WEIGHTS = {"POWL":0.12,"AMKR":0.12,"VST":0.11,"TLN":0.10,"PWR":0.10,
           "MOD":0.10,"NVT":0.10,"ETN":0.09,"CEG":0.08,"ITRI":0.08}

def px(sym, today):
    try:
        return fresh_price(sym, max_age_min=120)["price"]
    except Exception:
        d = daily_history(sym, period="5d")
        if d.index[-1].strftime("%Y-%m-%d") != today:
            raise RuntimeError(f"{sym}: no bar for {today}")
        return float(d["Close"].iloc[-1])

def main():
    today = datetime.now(ET).strftime("%Y-%m-%d")
    if STATE.exists():
        st = json.loads(STATE.read_text())
        v = st.get("cash", 0.0)
        for sym, pos in st.get("holdings", {}).items():
            try: v += pos["shares"] * px(sym, today)
            except Exception: v += pos["shares"] * pos["entry_px"]
        base = st.get("inception_value", NOTIONAL)
        print(f"[H6] {today} mark sleeve=${v:,.0f} ({(v/base-1)*1e4:+.0f}bps since {st.get('inception')})")
        return
    # 首建仓(市场开市日才执行)
    holdings, spent = {}, 0.0
    for sym, w in WEIGHTS.items():
        try:
            p = px(sym, today) * (1 + SLIP/1e4)
        except Exception as e:
            print(f"[H6] abort init: {sym} no fresh price ({e})"); return
        sh = int(NOTIONAL * w / p)
        holdings[sym] = {"shares": sh, "entry_px": round(p, 4)}
        spent += sh * p
    st = {"inception": today, "inception_value": NOTIONAL, "half_sized": True,
          "review": "2026-08-14 Q2 13F -> full or exit", "cash": round(NOTIONAL - spent, 2),
          "holdings": holdings}
    STATE.write_text(json.dumps(st, indent=1))
    log_event("h6_sleeve_init", st)
    print(f"[H6] INIT half-size ${spent:,.0f} deployed across {len(holdings)} names")

if __name__ == "__main__":
    main()
