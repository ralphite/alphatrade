"""价格数据层：yfinance 为主，带重试与缓存。持有期为小时~天，可容忍延迟报价。"""
import json
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "prices"
CACHE.mkdir(parents=True, exist_ok=True)


def _retry(fn, tries=3, wait=2.0):
    last = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(wait * (i + 1))
    raise last


def daily_history(ticker: str, period="6y") -> pd.DataFrame:
    """日线 OHLCV（auto_adjust=False，保留真实 Open/Close 供隔夜研究）。缓存当日有效。"""
    f = CACHE / f"{ticker}_daily_{period}.pkl"
    if f.exists() and time.time() - f.stat().st_mtime < 20 * 3600:
        return pd.read_pickle(f)
    df = _retry(lambda: yf.Ticker(ticker).history(period=period, auto_adjust=False))
    if df is None or df.empty:
        raise RuntimeError(f"no daily data for {ticker}")
    df.to_pickle(f)
    return df


def snapshot(ticker: str) -> dict:
    """当前快照：最新价、市值、货币、均量。用 fast_info，失败退回 history。"""
    t = yf.Ticker(ticker)

    def _get():
        fi = t.fast_info
        last = fi.last_price
        if last is None or not (last == last):
            raise RuntimeError("no last price")
        return {
            "ticker": ticker,
            "last": float(last),
            "market_cap": float(fi.market_cap) if fi.market_cap else None,
            "currency": fi.currency,
            "exchange": fi.exchange,
            "avg_vol_10d": float(fi.ten_day_average_volume) if fi.ten_day_average_volume else None,
            "ts": time.time(),
        }

    try:
        return _retry(_get, tries=2, wait=1.0)
    except Exception:
        h = _retry(lambda: t.history(period="5d"))
        if h is None or h.empty:
            raise RuntimeError(f"no snapshot for {ticker}")
        return {
            "ticker": ticker,
            "last": float(h["Close"].iloc[-1]),
            "market_cap": None,
            "currency": None,
            "exchange": None,
            "avg_vol_10d": float(h["Volume"].tail(5).mean()),
            "ts": time.time(),
        }


def adv_dollars(ticker: str, days=20, before_date=None) -> float:
    """20 日均成交额（美元）。before_date（YYYY-MM-DD）给定时只用该日之前的数据——
    事件驱动过滤必须用事件前 ADV，否则事件日放量会抬高流动性档位（红队 P1-4）。"""
    df = daily_history(ticker, period="6mo")
    if before_date:
        df = df[df.index.strftime("%Y-%m-%d") < before_date]
    tail = df.tail(days)
    if tail.empty:
        raise RuntimeError("no pre-event history")
    return float((tail["Close"] * tail["Volume"]).mean())


def fresh_price(ticker: str, max_age_min=25) -> dict:
    """带时间戳校验的最新价（红队 P1-5：fast_info.last 可能是隔夜前收且无时间戳）。
    用当日 1m bar 的最后一根，要求 bar 时间在 max_age_min 内。返回 {price, quote_ts, spread_bps?}。"""
    t = yf.Ticker(ticker)
    h = _retry(lambda: t.history(period="1d", interval="1m"))
    if h is None or h.empty:
        raise RuntimeError(f"no intraday bars for {ticker}")
    last_bar = h.index[-1]
    age_min = (pd.Timestamp.now(tz=last_bar.tz) - last_bar).total_seconds() / 60
    if age_min > max_age_min:
        raise RuntimeError(f"stale quote for {ticker}: last bar {last_bar} ({age_min:.0f}min old)")
    out = {"price": float(h["Close"].iloc[-1]), "quote_ts": str(last_bar), "age_min": round(age_min, 1)}
    try:
        fi = t.fast_info
        bid, ask = getattr(fi, "bid", None), getattr(fi, "ask", None)
        if bid and ask and ask > bid > 0:
            out["spread_bps"] = round((ask - bid) / ((ask + bid) / 2) * 1e4, 1)
    except Exception:  # noqa: BLE001
        pass
    return out


def intraday_bars(ticker: str, interval="5m"):
    """当日盘中 bars（用于止损穿越检测，红队 P1-6）。"""
    return _retry(lambda: yf.Ticker(ticker).history(period="1d", interval=interval))


def liquidity_gate(ticker: str, event_date=None, min_price=3.0, min_adv=2e6, max_mcap=5e10):
    """风控池检查。返回 (ok: bool, info: dict, reason: str)。
    红队 P1-4：价格与 ADV 一律用事件日**之前**的日线，防幸存者偏差与事件日放量污染。
    同时产出 prev_close（事件前收盘）与 chg_since_event_pct（当前价相对事件前收盘的涨跌，喂给评估者做 priced-in 判断，红队 P1-2）。"""
    try:
        df = daily_history(ticker, period="6mo")
    except Exception as e:  # noqa: BLE001
        return False, {}, f"no-data:{e}"
    pre = df[df.index.strftime("%Y-%m-%d") < event_date] if event_date else df
    if len(pre) < 20:
        return False, {}, "insufficient-history"
    prev_close = float(pre["Close"].iloc[-1])
    pre_adv = float((pre["Close"].tail(20) * pre["Volume"].tail(20)).mean())
    s = {"ticker": ticker, "prev_close": prev_close, "adv_dollars": pre_adv}
    try:
        snap = snapshot(ticker)
        s["last"] = snap["last"]
        s["market_cap"] = snap["market_cap"]
        s["chg_since_event_pct"] = round((snap["last"] / prev_close - 1) * 100, 2)
    except Exception:  # noqa: BLE001
        s["last"], s["market_cap"], s["chg_since_event_pct"] = prev_close, None, None
    if prev_close < min_price:
        return False, s, f"price<{min_price}"
    if pre_adv < min_adv:
        return False, s, "adv<2M"
    # market_cap 为 None 的基本是小票（大盘股 fast_info 稳定），megacap gate 不因 None 失效构成实际风险
    if s["market_cap"] and s["market_cap"] > max_mcap:
        return False, s, "megacap>50B"
    return True, s, "ok"


if __name__ == "__main__":
    spy = daily_history("SPY", period="1mo")
    print("SPY daily rows:", len(spy), "last close:", round(float(spy['Close'].iloc[-1]), 2))
    print("snapshot:", json.dumps(snapshot("SPY"), indent=1))
