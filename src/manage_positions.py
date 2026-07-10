"""持仓管理（红队修复版）：盘中 low 穿越止损（P1-6）+ T+N 收盘退出 + 影子仓同规则。

止损判定不再只看当下 last：检查入场以来当日 5m bars 的 low 是否触及 stop，
触及则以 min(触发 bar 的 open, stop_px) 为参考价成交（gap 直接吃 open，不假设限价保护）。
"""
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from data import daily_history, fresh_price, intraday_bars  # noqa: E402
from ledger import close_position, load_positions, log_event  # noqa: E402

ET = ZoneInfo("America/New_York")


def trading_days_after(entry_date: str):
    cal = [d.strftime("%Y-%m-%d") for d in daily_history("SPY", period="3mo").index]
    return [d for d in cal if d > entry_date]


def check_stop_cross(ticker: str, p: dict):
    """返回 (triggered, ref_price)。long: 当日 low<=stop；short: high>=stop。"""
    try:
        bars = intraday_bars(ticker, "5m")
    except Exception:  # noqa: BLE001
        return False, None
    if bars is None or bars.empty:
        return False, None
    entry_ts = p["entry_ts"]
    idx = bars.index.tz_convert("UTC") if bars.index.tz is not None else bars.index
    mask = [str(i) > entry_ts.replace("+00:00", "") for i in idx.strftime("%Y-%m-%dT%H:%M:%S")]
    bars = bars[mask] if any(mask) else bars.iloc[0:0]
    if bars.empty:
        return False, None
    if p["direction"] == "long":
        hit = bars[bars["Low"] <= p["stop_px"]]
        if not hit.empty:
            return True, min(float(hit["Open"].iloc[0]), p["stop_px"])
    else:
        hit = bars[bars["High"] >= p["stop_px"]]
        if not hit.empty:
            return True, max(float(hit["Open"].iloc[0]), p["stop_px"])
    return False, None


def spy_now():
    try:
        return fresh_price("SPY")["price"]
    except Exception:  # noqa: BLE001
        return None


def manage_book(shadow: bool, force_time_exit=False):
    pos = load_positions(shadow=shadow)
    if not pos:
        return
    now = datetime.now(ET)
    after_close = now.hour >= 16
    today = now.strftime("%Y-%m-%d")
    spy = spy_now()
    tag = "SHADOW" if shadow else "EXEC"
    for key, p in list(pos.items()):
        ticker = p["ticker"]
        try:
            fp = fresh_price(ticker, max_age_min=90 if after_close else 25)
        except Exception as e:  # noqa: BLE001
            print(f"[{tag}] {ticker:6s} mark-fail: {e}")
            continue
        last = fp["price"]
        meta = {"market_cap": p["signal"].get("market_cap"), "spread_bps": fp.get("spread_bps"), "quote_ts": fp["quote_ts"]}
        sign = 1 if p["direction"] == "long" else -1
        upnl_pct = sign * (last / p["entry_px"] - 1) * 100
        tds = trading_days_after(p["et_open_date"])
        held = len([d for d in tds if d <= today])
        due = held >= p["exit_after_close_n"] and (after_close or force_time_exit)
        log_event("mark", {"shadow": shadow, "ticker": ticker, "last": last,
                           "upnl_pct": round(upnl_pct, 2), "held_td": held})
        stopped, stop_ref = check_stop_cross(ticker, p)
        if stopped:
            t = close_position(key, stop_ref, meta, "stop", spy, shadow=shadow)
            print(f"[{tag}] {ticker:6s} STOP @ {t['exit_px']} pnl ${t['pnl']} excess {fmt_bps(t.get('excess_ret'))}")
        elif due:
            t = close_position(key, last, meta, "time", spy, shadow=shadow)
            print(f"[{tag}] {ticker:6s} TIME @ {t['exit_px']} pnl ${t['pnl']} excess {fmt_bps(t.get('excess_ret'))}")
        else:
            print(f"[{tag}] {ticker:6s} HOLD last {last:.2f} upnl {upnl_pct:+.1f}% held {held}/{p['exit_after_close_n']}")


def fmt_bps(x):
    return f"{x*1e4:+.0f}bps" if x is not None else "n/a"


def main(force_time_exit=False):
    manage_book(shadow=False, force_time_exit=force_time_exit)
    manage_book(shadow=True, force_time_exit=force_time_exit)
    if not load_positions() and not load_positions(shadow=True):
        print("no open positions (exec or shadow)")


if __name__ == "__main__":
    main(force_time_exit="--force-time-exit" in sys.argv)
