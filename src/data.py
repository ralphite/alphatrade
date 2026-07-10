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


def adv_dollars(ticker: str, days=20) -> float:
    """20 日均成交额（美元）。"""
    df = daily_history(ticker, period="3mo")
    tail = df.tail(days)
    return float((tail["Close"] * tail["Volume"]).mean())


def liquidity_gate(ticker: str, min_price=3.0, min_adv=2e6, max_mcap=5e10):
    """风控池检查。返回 (ok: bool, info: dict, reason: str)。ADV 用 10 日均量×现价估算，缺失才拉日线。"""
    try:
        s = snapshot(ticker)
    except Exception as e:  # noqa: BLE001
        return False, {}, f"no-data:{e}"
    if s["currency"] not in (None, "USD"):
        return False, s, "not-usd"
    if s["last"] < min_price:
        return False, s, f"price<{min_price}"
    adv = (s["avg_vol_10d"] or 0) * s["last"]
    if adv <= 0:
        try:
            adv = adv_dollars(ticker)
        except Exception as e:  # noqa: BLE001
            return False, s, f"no-adv:{e}"
    s["adv_dollars"] = adv
    if adv < min_adv:
        return False, s, "adv<2M"
    if s["market_cap"] and s["market_cap"] > max_mcap:
        return False, s, "megacap>50B"
    return True, s, "ok"


if __name__ == "__main__":
    spy = daily_history("SPY", period="1mo")
    print("SPY daily rows:", len(spy), "last close:", round(float(spy['Close'].iloc[-1]), 2))
    print("snapshot:", json.dumps(snapshot("SPY"), indent=1))
