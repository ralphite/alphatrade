"""H9 月末国债窗口 sleeve 执行器(daily_close 调用)。

规则(HYPOTHESES.md H9,预注册):每月倒数第 5 个交易日收盘买入 IEF(吃最后 4 个交易日的收益),
月末最后一个交易日收盘卖出。sleeve $20k,滑点 2bps/边。
状态:ledger/ief_sleeve.json;流水:ledger/ief_sleeve_trades.jsonl
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history, fresh_price  # noqa: E402
from ledger import log_event  # noqa: E402
from tom_sleeve import trading_days_of_month  # noqa: E402

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "ledger" / "ief_sleeve.json"
TRADES = ROOT / "ledger" / "ief_sleeve_trades.jsonl"
NOTIONAL = 20_000.0
SLIP_BPS = 2.0


def target(today: str) -> str:
    cur = trading_days_of_month(int(today[:4]), int(today[5:7]))
    if today not in cur:
        return "HOLD"
    # 倒数第5个交易日收盘买入,持有到月末最后一天收盘卖出
    return "IEF" if today >= cur[-5] and today != cur[-1] else ("SELL" if today == cur[-1] else "CASH")


def px(sym, today):
    try:
        return fresh_price(sym, max_age_min=120)["price"]
    except Exception:  # noqa: BLE001
        d = daily_history(sym, period="5d")
        if d.index[-1].strftime("%Y-%m-%d") != today:
            raise RuntimeError(f"{sym}: no bar for {today}")
        return float(d["Close"].iloc[-1])


def main():
    now = datetime.now(ET)
    today = now.strftime("%Y-%m-%d")
    tgt = target(today)
    st = json.loads(STATE.read_text()) if STATE.exists() else {"position": "CASH", "cash": NOTIONAL, "shares": 0}
    if tgt == "HOLD":
        print(f"[IEF] {today} non-trading day")
        return
    if tgt == "IEF" and st["position"] == "CASH":
        p = px("IEF", today) * (1 + SLIP_BPS / 1e4)
        shares = int(st["cash"] / p)
        st = {"position": "IEF", "shares": shares, "entry_px": round(p, 4),
              "cash": round(st["cash"] - shares * p, 2), "entry_date": today}
        STATE.write_text(json.dumps(st, indent=1))
        log_event("ief_sleeve_buy", st)
        print(f"[IEF] BUY {shares}sh @ {p:.2f}")
    elif tgt == "SELL" and st["position"] == "IEF":
        p = px("IEF", today) * (1 - SLIP_BPS / 1e4)
        proceeds = st["shares"] * p + st["cash"]
        trade = {"entry_date": st.get("entry_date"), "exit_date": today,
                 "entry_px": st.get("entry_px"), "exit_px": round(p, 4),
                 "ret_bps": round((p / st["entry_px"] - 1) * 1e4, 1), "sleeve_value": round(proceeds, 2)}
        with TRADES.open("a") as f:
            f.write(json.dumps(trade) + "\n")
        st = {"position": "CASH", "cash": round(proceeds, 2), "shares": 0}
        STATE.write_text(json.dumps(st, indent=1))
        log_event("ief_sleeve_sell", trade)
        print(f"[IEF] SELL @ {p:.2f} ret {trade['ret_bps']:+.1f}bps sleeve ${proceeds:,.0f}")
    else:
        v = st["cash"] + st["shares"] * (px("IEF", today) if st["position"] == "IEF" else 0)
        print(f"[IEF] {today} {st['position']} sleeve=${v:,.0f} (target {tgt})")


if __name__ == "__main__":
    main()
