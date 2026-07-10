"""持仓管理：检查止损与 T+N 收盘退出，mark-to-market。每次 loop 唤醒时运行。

退出规则（H1 v1，预注册）：
  - 最新价 <= stop_px → 立即平仓（reason=stop）
  - 从入场日起第 2 个交易日的收盘（>=16:00 ET）→ 平仓（reason=time）
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history, snapshot  # noqa: E402
from ledger import close_position, load_positions, log_event  # noqa: E402

ET = ZoneInfo("America/New_York")


def trading_days_since(entry_date: str):
    """从 SPY 日线索引取交易日历，返回 entry 之后的交易日序列（date 字符串）。"""
    cal = [d.strftime("%Y-%m-%d") for d in daily_history("SPY", period="3mo").index]
    return [d for d in cal if d > entry_date]


def main(force_time_exit=False):
    pos = load_positions()
    if not pos:
        print("no open positions")
        return
    now = datetime.now(ET)
    after_close = now.hour >= 16
    today = now.strftime("%Y-%m-%d")
    for ticker, p in list(pos.items()):
        try:
            snap = snapshot(ticker)
        except Exception as e:  # noqa: BLE001
            print(f"{ticker:6s} mark-fail: {e}")
            continue
        last = snap["last"]
        adv = (snap.get("avg_vol_10d") or 0) * last
        upnl_pct = (last / p["entry_px"] - 1) * 100
        entry_date = p["entry_ts"][:10]
        tds = trading_days_since(entry_date)
        held_days = len([d for d in tds if d <= today])
        due = held_days >= p["exit_after_close_n"] and (after_close or force_time_exit)
        log_event("mark", {"ticker": ticker, "last": last, "upnl_pct": round(upnl_pct, 2), "held_td": held_days})
        if last <= p["stop_px"]:
            t = close_position(ticker, last, adv, "stop")
            print(f"{ticker:6s} STOP-EXIT @ {t['exit_px']} pnl ${t['pnl']} ({t['ret_net']*1e4:.0f}bps)")
        elif due:
            t = close_position(ticker, last, adv, "time")
            print(f"{ticker:6s} TIME-EXIT @ {t['exit_px']} pnl ${t['pnl']} ({t['ret_net']*1e4:.0f}bps)")
        else:
            print(f"{ticker:6s} HOLD  last {last:.2f}  upnl {upnl_pct:+.1f}%  held_td {held_days}/{p['exit_after_close_n']}")


if __name__ == "__main__":
    main(force_time_exit="--force-time-exit" in sys.argv)
