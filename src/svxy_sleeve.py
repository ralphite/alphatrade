"""H12 VIX carry sleeve 执行器(daily_close 调用)。
规则:昨收 VIX<VIX3M → 持 SVXY;否则现金。$10k sleeve,滑点 5bps/边。
"""
import json, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0, str(Path(__file__).parent))
import yfinance as yf
from data import daily_history, fresh_price
from ledger import log_event

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "ledger" / "svxy_sleeve.json"
TRADES = ROOT / "ledger" / "svxy_sleeve_trades.jsonl"
NOTIONAL = 10_000.0
SLIP = 5.0

def idx_close(sym):
    h = yf.Ticker(sym).history(period="5d")["Close"]
    return float(h.iloc[-1]), h.index[-1].strftime("%Y-%m-%d")

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
    vix, dv = idx_close("^VIX")
    v3m, d3 = idx_close("^VIX3M")
    contango = vix < v3m
    st = json.loads(STATE.read_text()) if STATE.exists() else {"position": "CASH", "cash": NOTIONAL, "shares": 0}
    if contango and st["position"] == "CASH":
        p = px("SVXY", today) * (1 + SLIP/1e4)
        sh = int(st["cash"] / p)
        st = {"position": "SVXY", "shares": sh, "entry_px": round(p,4), "cash": round(st["cash"]-sh*p,2), "entry_date": today}
        STATE.write_text(json.dumps(st, indent=1)); log_event("svxy_buy", {**st, "vix": vix, "v3m": v3m})
        print(f"[SVXY] BUY {sh}sh @ {p:.2f} (VIX {vix:.1f} < VIX3M {v3m:.1f})")
    elif not contango and st["position"] == "SVXY":
        p = px("SVXY", today) * (1 - SLIP/1e4)
        proceeds = st["shares"]*p + st["cash"]
        tr = {"entry_date": st.get("entry_date"), "exit_date": today, "entry_px": st.get("entry_px"),
              "exit_px": round(p,4), "ret_bps": round((p/st["entry_px"]-1)*1e4,1), "sleeve_value": round(proceeds,2)}
        with TRADES.open("a") as f: f.write(json.dumps(tr)+"\n")
        st = {"position": "CASH", "cash": round(proceeds,2), "shares": 0}
        STATE.write_text(json.dumps(st, indent=1)); log_event("svxy_sell", {**tr, "vix": vix, "v3m": v3m})
        print(f"[SVXY] SELL @ {p:.2f} ret {tr['ret_bps']:+.0f}bps (backwardation: VIX {vix:.1f} >= {v3m:.1f})")
    else:
        v = st["cash"] + (st["shares"]*px("SVXY", today) if st["position"]=="SVXY" else 0)
        print(f"[SVXY] {today} {st['position']} sleeve=${v:,.0f} VIX {vix:.1f}/{v3m:.1f} {'contango' if contango else 'BACKWARDATION'}")

if __name__ == "__main__":
    main()
