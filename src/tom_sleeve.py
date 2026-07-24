"""H4c TOM 轮动 sleeve 的 paper 执行器。每个交易日收盘后运行一次（收盘轮调用）。

规则（HYPOTHESES.md H4c，预注册）：
  - 月末倒数第 2 个交易日收盘：QQQ → QLD
  - 次月第 2 个交易日收盘：QLD → QQQ
  - sleeve 名义 $30k（总 $100k 的 30%），滑点 2bps/边
状态：ledger/tom_sleeve.json；流水：ledger/tom_sleeve_trades.jsonl
"""
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history, fresh_price  # noqa: E402
from ledger import log_event  # noqa: E402

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "ledger" / "tom_sleeve.json"
TRADES = ROOT / "ledger" / "tom_sleeve_trades.jsonl"
SLEEVE_NOTIONAL = 30_000.0
SLIP_BPS = 2.0
HOLIDAYS = {"2026-09-07", "2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18"}


def trading_days_of_month(y, m):
    d = date(y, m, 1)
    out = []
    while d.month == m:
        if d.weekday() < 5 and d.strftime("%Y-%m-%d") not in HOLIDAYS:
            out.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    return out


def target_position(today: str) -> str:
    """今天收盘后应持有什么（回测口径 TOM(2,2)：收益日=月末最后2交易日+月初头2交易日；
    故买入=倒数第3交易日收盘，卖出=次月第2交易日收盘）。"""
    y, m = int(today[:4]), int(today[5:7])
    cur = trading_days_of_month(y, m)
    if today not in cur:
        return "HOLD"  # 非交易日
    if today >= cur[-3]:
        return "QLD"   # 倒数第3交易日收盘买入，持有月末最后2天的收益
    if today < cur[1]:
        return "QLD"   # 月初第1交易日收盘后仍持有
    if today == cur[1]:
        return "QQQ"   # 第2交易日收盘卖出（已吃到当日收益）
    return "QQQ"


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return None


def mark(px_qqq, px_qld, st):
    px = px_qld if st["position"] == "QLD" else px_qqq
    return round(st["shares"] * px + st.get("cash", 0.0), 2)


def main():
    now = datetime.now(ET)
    today = now.strftime("%Y-%m-%d")
    tgt = target_position(today)

    def px(sym):
        """收盘轮取价：fresh_price 优先，stale 则退回当日日线收盘（收盘后执行对时刻不敏感）。"""
        try:
            return fresh_price(sym, max_age_min=120)["price"]
        except Exception:  # noqa: BLE001
            d = daily_history(sym, period="5d")
            if d.index[-1].strftime("%Y-%m-%d") != today:
                raise RuntimeError(f"{sym}: no bar for {today} (market closed?)")
            return float(d["Close"].iloc[-1])

    qqq = px("QQQ")
    qld = px("QLD")
    st = load_state()
    if st is None:
        # 初始化：按当日目标建仓
        pos = tgt if tgt in ("QQQ", "QLD") else "QQQ"
        px = (qld if pos == "QLD" else qqq) * (1 + SLIP_BPS / 1e4)
        shares = int(SLEEVE_NOTIONAL / px)
        st = {"position": pos, "shares": shares, "entry_px": round(px, 4),
              "cash": round(SLEEVE_NOTIONAL - shares * px, 2),
              "inception": today, "inception_value": SLEEVE_NOTIONAL,
              "qqq_inception_px": qqq, "last_action": today}
        STATE.write_text(json.dumps(st, indent=1))
        log_event("tom_sleeve_init", st)
        print(f"[TOM] init: {pos} {shares}sh @ {px:.2f}")
        return
    if tgt == "HOLD":
        print(f"[TOM] {today} non-trading day")
        return
    if tgt != st["position"]:
        # 换仓：卖旧买新，各收滑点
        sell_px = (qld if st["position"] == "QLD" else qqq) * (1 - SLIP_BPS / 1e4)
        proceeds = st["shares"] * sell_px + st.get("cash", 0.0)
        buy_px = (qld if tgt == "QLD" else qqq) * (1 + SLIP_BPS / 1e4)
        shares = int(proceeds / buy_px)
        trade = {"date": today, "from": st["position"], "to": tgt,
                 "sell_px": round(sell_px, 4), "buy_px": round(buy_px, 4),
                 "shares": shares, "sleeve_value": round(proceeds, 2)}
        with TRADES.open("a") as f:
            f.write(json.dumps(trade) + "\n")
        st.update({"position": tgt, "shares": shares, "entry_px": round(buy_px, 4),
                   "cash": round(proceeds - shares * buy_px, 2), "last_action": today})
        STATE.write_text(json.dumps(st, indent=1))
        log_event("tom_sleeve_switch", trade)
        print(f"[TOM] SWITCH {trade['from']}->{tgt} {shares}sh @ {buy_px:.2f} sleeve=${proceeds:,.0f}")
    else:
        v = mark(qqq, qld, st)
        bench = SLEEVE_NOTIONAL * qqq / st["qqq_inception_px"]
        print(f"[TOM] {today} hold {st['position']} sleeve=${v:,.0f} vs QQQ-bench=${bench:,.0f} excess={((v/bench)-1)*1e4:+.0f}bps")
        log_event("tom_sleeve_mark", {"value": v, "bench": round(bench, 2)})


if __name__ == "__main__":
    main()
