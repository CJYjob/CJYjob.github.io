#!/usr/bin/env python3
"""Daily investment information/analysis automation.

This script never places orders. It only collects public/credentialed market
information, produces analysis support artifacts, and evaluates prior analysis.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "investment_config.json"
DAILY_PATH = ROOT / "data" / "investment_daily.json"
PERFORMANCE_PATH = ROOT / "data" / "investment_performance.json"
LOG_ROOT = ROOT / "content" / "ko" / "log" / "etf-live-trading"
KST = ZoneInfo("Asia/Seoul")
USER_AGENT = "CJYjob-investment-automation/1.0"

ALLOWED_ACTIONS = {"BUY", "SELL", "HOLD", "WAIT"}
ALLOWED_DIRECTIONS = {"UP", "NEUTRAL", "DOWN"}


def now_kst() -> datetime:
    return datetime.now(tz=KST)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(temp, path)


def safe_float(value: Any) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def pct(value: float | None) -> str:
    return "N/A" if value is None else f"{value * 100:.2f}%"


def money(value: float | None) -> str:
    return "N/A" if value is None else f"{value:,.0f}"


def latest_value(series: pd.Series) -> float | None:
    s = pd.to_numeric(series, errors="coerce").dropna()
    return safe_float(s.iloc[-1]) if len(s) else None


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50.0)


def atr(frame: pd.DataFrame, window: int = 14) -> pd.Series:
    prev_close = frame["Close"].shift(1)
    tr = pd.concat(
        [
            frame["High"] - frame["Low"],
            (frame["High"] - prev_close).abs(),
            (frame["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def adx(frame: pd.DataFrame, window: int = 14) -> pd.Series:
    high, low, close = frame["High"], frame["Low"], frame["Close"]
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=frame.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=frame.index)
    atr_values = atr(frame, window)
    plus_di = 100 * plus_dm.ewm(alpha=1 / window, adjust=False).mean() / atr_values.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / window, adjust=False).mean() / atr_values.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def compute_indicators(frame: pd.DataFrame) -> dict[str, Any]:
    close = frame["Close"].astype(float)
    result: dict[str, Any] = {}
    for window in (5, 10, 20, 60, 120):
        result[f"sma_{window}"] = latest_value(close.rolling(window).mean())
    result["ema_12"] = latest_value(ema(close, 12))
    result["ema_26"] = latest_value(ema(close, 26))

    macd_line = ema(close, 12) - ema(close, 26)
    macd_signal = ema(macd_line, 9)
    result["macd"] = latest_value(macd_line)
    result["macd_signal"] = latest_value(macd_signal)
    result["macd_histogram"] = latest_value(macd_line - macd_signal)
    result["rsi_14"] = latest_value(rsi(close, 14))
    result["atr_14"] = latest_value(atr(frame, 14))
    result["adx_14"] = latest_value(adx(frame, 14))
    result["roc_10"] = latest_value(close.pct_change(10))

    mid = close.rolling(20).mean()
    sd = close.rolling(20).std(ddof=0)
    upper = mid + 2 * sd
    lower = mid - 2 * sd
    result["bb_lower"] = latest_value(lower)
    result["bb_mid"] = latest_value(mid)
    result["bb_upper"] = latest_value(upper)
    current = latest_value(close)
    if current is not None and result["bb_lower"] is not None and result["bb_upper"] is not None:
        width = result["bb_upper"] - result["bb_lower"]
        result["bb_percent_b"] = (current - result["bb_lower"]) / width if width > 0 else None
        result["bb_bandwidth"] = width / result["bb_mid"] if result["bb_mid"] else None
    else:
        result["bb_percent_b"] = None
        result["bb_bandwidth"] = None
    return result


def projected_indicator_ranges(
    close_history: np.ndarray,
    predicted_low: float,
    predicted_high: float,
    ma_windows: tuple[int, ...] = (5, 10, 20, 60, 120),
    bb_window: int = 20,
    bb_k: float = 2.0,
) -> dict[str, list[float]]:
    """Port of the Colab helper: indicator values if next close spans forecast low~high."""
    close = np.asarray(close_history, float)

    def calc(candidate: float) -> dict[str, float]:
        x = np.append(close, candidate)
        mas = {f"ma{w}": float(np.mean(x[-w:])) for w in ma_windows if len(x) >= w}
        b = x[-bb_window:]
        mid = float(np.mean(b))
        sd = float(np.std(b, ddof=0))
        return {**mas, "bb_lower": mid - bb_k * sd, "bb_mid": mid, "bb_upper": mid + bb_k * sd}

    low_case, high_case = calc(predicted_low), calc(predicted_high)
    return {
        key: [min(low_case[key], high_case[key]), max(low_case[key], high_case[key])]
        for key in sorted(low_case.keys() & high_case.keys())
    }


def empirical_next_session_forecast(frame: pd.DataFrame, lookback: int = 504) -> dict[str, Any]:
    """Leakage-free empirical next-session OHLC quantiles relative to prior close."""
    if len(frame) < 130:
        raise ValueError(f"insufficient market history: {len(frame)} rows")
    x = frame.tail(lookback + 1).copy()
    prior_close = x["Close"].shift(1)
    samples = pd.DataFrame(
        {
            "open_r": x["Open"] / prior_close - 1,
            "high_r": x["High"] / prior_close - 1,
            "low_r": x["Low"] / prior_close - 1,
            "close_r": x["Close"] / prior_close - 1,
        }
    ).dropna()
    if len(samples) < 100:
        raise ValueError(f"insufficient forecast samples: {len(samples)}")

    current = float(x["Close"].iloc[-1])
    qs = (0.10, 0.25, 0.50, 0.75, 0.90)
    quantiles = {
        col: {f"q{int(q*100):02d}": float(samples[col].quantile(q)) for q in qs}
        for col in samples.columns
    }
    predicted_low = current * (1 + quantiles["low_r"]["q10"])
    predicted_high = current * (1 + quantiles["high_r"]["q90"])
    median_close_return = quantiles["close_r"]["q50"]

    neutral_threshold = max(0.0025, float(samples["close_r"].abs().median()) * 0.20)
    if median_close_return > neutral_threshold:
        direction = "UP"
    elif median_close_return < -neutral_threshold:
        direction = "DOWN"
    else:
        direction = "NEUTRAL"

    return {
        "method": "empirical_next_session_quantiles",
        "sample_count": int(len(samples)),
        "reference_close": current,
        "predicted_range": {"low": predicted_low, "high": predicted_high},
        "close_scenarios": {
            "bear": current * (1 + quantiles["close_r"]["q25"]),
            "base": current * (1 + quantiles["close_r"]["q50"]),
            "bull": current * (1 + quantiles["close_r"]["q75"]),
        },
        "direction": direction,
        "neutral_threshold": neutral_threshold,
        "quantile_returns": quantiles,
        "uncertainty": {
            "close_q10_q90_width": quantiles["close_r"]["q90"] - quantiles["close_r"]["q10"],
            "range_width_pct": predicted_high / predicted_low - 1 if predicted_low > 0 else None,
            "note": "Historical empirical quantiles are a baseline, not a guarantee. Colab LSTM checkpoints are not stored in this repository.",
        },
    }


def normalize_yf_frame(raw: pd.DataFrame) -> pd.DataFrame:
    if raw is None or raw.empty:
        raise ValueError("market provider returned no rows")
    frame = raw.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [str(c[0]) for c in frame.columns]
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise ValueError(f"market data missing columns: {missing}")
    frame = frame[required].apply(pd.to_numeric, errors="coerce").dropna(subset=["Open", "High", "Low", "Close"])
    frame = frame[frame["Volume"].fillna(0) >= 0]
    if frame.empty:
        raise ValueError("market data empty after normalization")
    return frame


KRX_URL = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
KRX_HOME = "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101"
KRX_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Referer": "https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd",
    "X-Requested-With": "XMLHttpRequest",
}
KRX_SESSION = requests.Session()
KRX_SEEDED = False


def krx_number(value: Any) -> float:
    if value is None:
        return float("nan")
    text = str(value).strip().replace(",", "")
    if text in ("", "-", "N/A", "null"):
        return float("nan")
    return float(text)


def isin_check(base11: str) -> int:
    expanded = "".join(str(ord(c) - 55) if c.isalpha() else c for c in base11)
    total = 0
    for i, ch in enumerate(reversed(expanded)):
        digit = int(ch)
        if i % 2 == 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return (10 - (total % 10)) % 10


def krx_isin(code: str) -> str:
    code = str(code).strip().zfill(6)
    base = "KR7" + code + "00"
    return base + str(isin_check(base))


def krx_seed_session() -> None:
    global KRX_SEEDED
    if KRX_SEEDED:
        return
    try:
        KRX_SESSION.get(KRX_HOME, headers=KRX_HEADERS, timeout=10)
    finally:
        KRX_SEEDED = True


def krx_post(bld: str, **params: Any) -> dict[str, Any]:
    krx_seed_session()
    payload = dict(params)
    payload["bld"] = bld
    last: Exception | None = None
    for attempt in range(3):
        try:
            response = KRX_SESSION.post(KRX_URL, data=payload, headers=KRX_HEADERS, timeout=20)
            response.raise_for_status()
            text = response.text.strip()
            if text in ("", "LOGOUT") or text.startswith("<"):
                raise RuntimeError("KRX returned a non-JSON session response")
            return response.json()
        except Exception as exc:
            last = exc
            if attempt == 2:
                break
    raise RuntimeError(f"KRX request failed: {type(last).__name__ if last else 'unknown'}")


def krx_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("output", "OutBlock_1", "block1"):
        rows = payload.get(key)
        if isinstance(rows, list) and rows:
            return rows
    return []


def fetch_krx_ohlcv(code: str, start: str, end: str) -> pd.DataFrame:
    start_dt = pd.Timestamp(start)
    end_dt = pd.Timestamp(end)
    rows: list[dict[str, Any]] = []
    cursor = start_dt
    while cursor <= end_dt:
        chunk_end = min(cursor + pd.Timedelta(days=720), end_dt)
        payload = krx_post(
            "dbms/MDC/STAT/standard/MDCSTAT04501",
            strtDd=cursor.strftime("%Y%m%d"),
            endDd=chunk_end.strftime("%Y%m%d"),
            isuCd=krx_isin(code),
        )
        rows.extend(krx_rows(payload))
        cursor = chunk_end + pd.Timedelta(days=1)
    if not rows:
        raise ValueError("KRX returned no OHLCV rows")
    raw = pd.DataFrame(rows)
    frame = pd.DataFrame(
        {
            "Date": pd.to_datetime(raw["TRD_DD"].str.replace("/", "", regex=False), format="%Y%m%d"),
            "Open": raw["TDD_OPNPRC"].map(krx_number),
            "High": raw["TDD_HGPRC"].map(krx_number),
            "Low": raw["TDD_LWPRC"].map(krx_number),
            "Close": raw["TDD_CLSPRC"].map(krx_number),
            "Volume": raw["ACC_TRDVOL"].map(krx_number),
        }
    ).set_index("Date")
    return normalize_yf_frame(frame.sort_index())


def fetch_market_history(instrument: dict[str, Any], start: str | None = None, end: str | None = None) -> tuple[pd.DataFrame, str]:
    end_date = pd.Timestamp(end or now_kst().date().isoformat())
    start_date = pd.Timestamp(start) if start else end_date - pd.Timedelta(days=2200)
    try:
        frame = fetch_krx_ohlcv(instrument["code"], start_date.date().isoformat(), end_date.date().isoformat())
        return frame, "KRX Information Data System"
    except Exception:
        kwargs: dict[str, Any] = {
            "interval": "1d",
            "auto_adjust": False,
            "actions": False,
            "progress": False,
            "threads": False,
            "timeout": 30,
        }
        if start or end:
            kwargs["start"] = start_date.date().isoformat()
            kwargs["end"] = (end_date + pd.Timedelta(days=1)).date().isoformat()
        else:
            kwargs["period"] = "5y"
        raw = yf.download(instrument["ticker"], **kwargs)
        return normalize_yf_frame(raw), "Yahoo Finance fallback"


def collect_market(config: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = []
    for instrument in config["instruments"]:
        ticker = instrument["ticker"]
        try:
            frame, provider = fetch_market_history(instrument)
            indicators = compute_indicators(frame)
            forecast = empirical_next_session_forecast(frame, int(config.get("forecast_lookback_sessions", 504)))
            projected = projected_indicator_ranges(
                frame["Close"].to_numpy(float),
                forecast["predicted_range"]["low"],
                forecast["predicted_range"]["high"],
            )
            latest_date = pd.Timestamp(frame.index[-1]).date().isoformat()
            current_price = float(frame["Close"].iloc[-1])
            outputs.append(
                {
                    "name": instrument["name"],
                    "code": instrument["code"],
                    "ticker": ticker,
                    "market_data_source": provider,
                    "latest_market_date": latest_date,
                    "current_price": current_price,
                    "indicators": indicators,
                    "forecast": forecast,
                    "projected_indicator_ranges": projected,
                    "status": "ok",
                }
            )
        except Exception as exc:
            outputs.append(
                {
                    "name": instrument["name"],
                    "code": instrument["code"],
                    "ticker": ticker,
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return outputs


def fred_latest(series_id: str, api_key: str) -> dict[str, Any]:
    url = "https://api.stlouisfed.org/fred/series/observations"
    response = requests.get(
        url,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 10,
        },
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )
    response.raise_for_status()
    observations = response.json().get("observations", [])
    for item in observations:
        if item.get("value") not in (None, "."):
            return {"date": item.get("date"), "value": safe_float(item.get("value"))}
    raise ValueError(f"no usable FRED observation for {series_id}")


def collect_macro(config: dict[str, Any]) -> dict[str, Any]:
    key = os.environ.get("FRED_API_KEY")
    if not key:
        return {"status": "unavailable", "reason": "FRED_API_KEY is not configured", "indicators": []}
    rows = []
    for item in config.get("macro_indicators", []):
        try:
            value = fred_latest(item["series_id"], key)
            rows.append({**item, **value, "status": "ok"})
        except Exception as exc:
            rows.append({**item, "status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return {"status": "ok" if any(r.get("status") == "ok" for r in rows) else "error", "indicators": rows}


def collect_news_newsapi(config: dict[str, Any], key: str) -> list[dict[str, Any]]:
    query = config.get("news_query", "KOSPI OR Korea economy OR global markets")
    params = {
        "q": query,
        "language": config.get("news_language", "en"),
        "sortBy": "publishedAt",
        "pageSize": int(config.get("news_max_items", 10)),
        "apiKey": key,
    }
    domains = config.get("news_domains")
    if domains:
        params["domains"] = ",".join(domains)
    response = requests.get(
        "https://newsapi.org/v2/everything",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=25,
    )
    response.raise_for_status()
    articles = []
    for a in response.json().get("articles", []):
        articles.append(
            {
                "title": a.get("title"),
                "source": (a.get("source") or {}).get("name"),
                "published_at": a.get("publishedAt"),
                "url": a.get("url"),
                "description": a.get("description"),
            }
        )
    return articles


def collect_news_google_rss(config: dict[str, Any]) -> list[dict[str, Any]]:
    query = config.get("fallback_news_query", "KOSPI OR South Korea economy when:1d")
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=25)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    items = []
    for item in root.findall(".//item")[: int(config.get("news_max_items", 10))]:
        source_node = item.find("source")
        items.append(
            {
                "title": item.findtext("title"),
                "source": source_node.text if source_node is not None else None,
                "published_at": item.findtext("pubDate"),
                "url": item.findtext("link"),
                "description": None,
            }
        )
    return items


def collect_news(config: dict[str, Any]) -> dict[str, Any]:
    key = os.environ.get("NEWS_API_KEY")
    try:
        if key:
            articles = collect_news_newsapi(config, key)
            provider = "NewsAPI"
        else:
            articles = collect_news_google_rss(config)
            provider = "Google News RSS fallback"
        return {"status": "ok", "provider": provider, "articles": articles}
    except Exception as exc:
        return {"status": "error", "provider": "NewsAPI" if key else "Google News RSS fallback", "articles": [], "error": f"{type(exc).__name__}: {exc}"}


def extract_response_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    chunks: list[str] = []
    for output in payload.get("output", []):
        if output.get("type") != "message":
            continue
        for content in output.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    return "\n".join(chunks).strip()


def call_llm(system_prompt: str, user_payload: dict[str, Any], config: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None, "OPENAI_API_KEY is not configured"
    model = config.get("llm_model", "gpt-5-mini")
    body = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": json.dumps(user_payload, ensure_ascii=False)}]},
        ],
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": USER_AGENT},
            json=body,
            timeout=120,
        )
        response.raise_for_status()
        text = extract_response_text(response.json())
        if text.startswith("```"):
            text = text.strip("`")
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip()
        return json.loads(text), "ok"
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def deterministic_morning_analysis(market: list[dict[str, Any]], macro: dict[str, Any], news: dict[str, Any]) -> dict[str, Any]:
    strategies = []
    for item in market:
        if item.get("status") != "ok":
            continue
        direction = item["forecast"]["direction"]
        action = {"UP": "BUY", "DOWN": "SELL", "NEUTRAL": "WAIT"}[direction]
        strategies.append(
            {
                "instrument": item["name"],
                "action": action,
                "reason": f"Baseline D1 forecast direction={direction}; current technical indicators require human review.",
                "invalidation": f"Actual session trades outside forecast {item['forecast']['predicted_range']['low']:.0f}~{item['forecast']['predicted_range']['high']:.0f} or macro/news context materially changes.",
                "risks": ["Empirical range can fail in gap events", "No order is executed by this automation"],
            }
        )
    return {
        "market_summary": "Rule-based fallback because LLM output is unavailable.",
        "macro_state": "Review collected macro indicators; missing indicators are not imputed.",
        "strategies": strategies,
        "study": {
            "concept": "예측 구간과 변동성",
            "explanation": "익일 가격 범위는 점 하나보다 불확실성을 드러낸다. 범위 폭이 넓을수록 변동성 또는 모델 불확실성이 큰 것으로 보고 판단 강도를 낮춘다.",
        },
        "uncertainty": ["LLM synthesis unavailable; deterministic fallback used."],
    }


MORNING_SYSTEM_PROMPT = """You are an investment-analysis assistant. You do not place orders and do not claim certainty.
Analyze only the supplied technical results, macro data, and news. Existing risk rules take priority over your output.
Return ONE valid JSON object and no markdown with this schema:
{
  "market_summary": "short Korean summary",
  "macro_state": "short Korean summary",
  "strategies": [
    {
      "instrument": "exact supplied instrument name",
      "action": "BUY|SELL|HOLD|WAIT",
      "reason": "Korean reason",
      "invalidation": "Korean invalidation condition",
      "risks": ["Korean risk", "..."]
    }
  ],
  "study": {"concept": "Korean concept title", "explanation": "2-4 sentence Korean explanation tied to today's data/news"},
  "uncertainty": ["Korean uncertainty item", "..."]
}
Never fabricate missing values or user trades. A BUY/SELL label is a decision-support candidate, not an order.
"""

EVENING_SYSTEM_PROMPT = """You are reviewing a morning investment analysis against actual market results.
Do not invent user trades. If user_action is null, state that actual user action is unknown.
Return ONE valid JSON object and no markdown with this schema:
{
  "summary": "short Korean review",
  "good_judgments": ["..."],
  "wrong_judgments": ["..."],
  "error_candidates": ["..."],
  "next_adjustments": ["..."],
  "principle_review": "Korean text; only assess explicit user_action/principle fields, otherwise say not assessable"
}
Do not evaluate success from profit alone. Focus on forecast calibration, process, and rule adherence.
"""


def validate_strategy_analysis(analysis: dict[str, Any], market: list[dict[str, Any]]) -> dict[str, Any]:
    names = {m["name"] for m in market if m.get("status") == "ok"}
    strategies = []
    for s in analysis.get("strategies", []):
        if s.get("instrument") not in names:
            continue
        action = str(s.get("action", "WAIT")).upper()
        if action not in ALLOWED_ACTIONS:
            action = "WAIT"
        strategies.append(
            {
                "instrument": s["instrument"],
                "action": action,
                "reason": str(s.get("reason", "")),
                "invalidation": str(s.get("invalidation", "")),
                "risks": [str(x) for x in s.get("risks", [])][:6],
            }
        )
    analysis["strategies"] = strategies
    return analysis


def find_daily(records: list[dict[str, Any]], date: str) -> dict[str, Any] | None:
    return next((r for r in records if r.get("date") == date), None)


def upsert_daily(records: list[dict[str, Any]], record: dict[str, Any]) -> list[dict[str, Any]]:
    out = [r for r in records if r.get("date") != record.get("date")]
    out.append(record)
    out.sort(key=lambda r: r.get("date", ""))
    return out


def strategy_map(morning: dict[str, Any]) -> dict[str, str]:
    return {x["instrument"]: x["action"] for x in morning.get("llm_analysis", {}).get("strategies", [])}


def morning_cycle(config: dict[str, Any], date: str) -> dict[str, Any]:
    market = collect_market(config)
    macro = collect_macro(config)
    news = collect_news(config)
    llm_payload = {"analysis_date": date, "market": market, "macro": macro, "news": news}
    llm_analysis, llm_status = call_llm(MORNING_SYSTEM_PROMPT, llm_payload, config)
    if not isinstance(llm_analysis, dict):
        llm_analysis = deterministic_morning_analysis(market, macro, news)
    llm_analysis = validate_strategy_analysis(llm_analysis, market)
    return {
        "generated_at": now_kst().isoformat(timespec="seconds"),
        "analysis_date": date,
        "analysis_target": [m.get("name") for m in market if m.get("status") == "ok"],
        "market": market,
        "macro": macro,
        "news": news,
        "llm_status": llm_status,
        "llm_analysis": llm_analysis,
        "colab_migration": {
            "ported": ["D1 range output", "moving-average/Bollinger projected ranges", "indicator calculation", "uncertainty fields"],
            "pending": ["Pooled LSTM model A/B inference because repository has no training workbook or model checkpoints"],
        },
    }


def market_actual_for_date(config: dict[str, Any], date: str) -> list[dict[str, Any]]:
    output = []
    target = pd.Timestamp(date)
    for instrument in config["instruments"]:
        try:
            frame, provider = fetch_market_history(
                instrument,
                start=(target - pd.Timedelta(days=5)).date().isoformat(),
                end=(target + pd.Timedelta(days=1)).date().isoformat(),
            )
            idx_dates = pd.Index(pd.to_datetime(frame.index).date)
            mask = idx_dates == target.date()
            if not mask.any():
                output.append({"name": instrument["name"], "status": "unavailable", "reason": "target market date not published by provider"})
                continue
            row = frame.loc[mask].iloc[-1]
            output.append(
                {
                    "name": instrument["name"],
                    "code": instrument["code"],
                    "status": "ok",
                    "market_date": date,
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                }
            )
        except Exception as exc:
            output.append({"name": instrument["name"], "status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return output


def evaluate_morning(morning: dict[str, Any], actuals: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    actual_map = {x["name"]: x for x in actuals if x.get("status") == "ok"}
    action_by_name = strategy_map(morning)
    evaluations = []
    neutral_floor = float(config.get("performance_neutral_threshold", 0.0025))
    for pred in morning.get("market", []):
        if pred.get("status") != "ok" or pred["name"] not in actual_map:
            continue
        actual = actual_map[pred["name"]]
        ref = float(pred["forecast"]["reference_close"])
        actual_return = actual["close"] / ref - 1
        direction = pred["forecast"]["direction"]
        threshold = max(neutral_floor, float(pred["forecast"].get("neutral_threshold") or 0))
        if actual_return > threshold:
            actual_direction = "UP"
        elif actual_return < -threshold:
            actual_direction = "DOWN"
        else:
            actual_direction = "NEUTRAL"
        p_low = float(pred["forecast"]["predicted_range"]["low"])
        p_high = float(pred["forecast"]["predicted_range"]["high"])
        range_hit = actual["low"] >= p_low and actual["high"] <= p_high
        close_in_range = p_low <= actual["close"] <= p_high
        errors = []
        if direction != actual_direction:
            errors.append("direction_miss")
        if not range_hit:
            errors.append("range_miss")
            if actual["high"] > p_high or actual["low"] < p_low:
                errors.append("volatility_underestimated")
        evaluations.append(
            {
                "instrument": pred["name"],
                "reference_close": ref,
                "predicted_direction": direction,
                "actual_direction": actual_direction,
                "direction_hit": direction == actual_direction,
                "predicted_low": p_low,
                "predicted_high": p_high,
                "actual_open": actual["open"],
                "actual_high": actual["high"],
                "actual_low": actual["low"],
                "actual_close": actual["close"],
                "actual_close_return": actual_return,
                "range_hit": range_hit,
                "close_in_range": close_in_range,
                "morning_strategy": action_by_name.get(pred["name"]),
                "error_tags": errors,
            }
        )
    return evaluations


def evening_cycle(config: dict[str, Any], date: str, existing: dict[str, Any]) -> dict[str, Any]:
    morning = existing.get("morning")
    if not morning:
        return {
            "generated_at": now_kst().isoformat(timespec="seconds"),
            "analysis_date": date,
            "status": "skipped",
            "reason": "morning result not found",
        }
    actuals = market_actual_for_date(config, date)
    evaluations = evaluate_morning(morning, actuals, config)
    user_action = existing.get("user_action")
    llm_payload = {
        "analysis_date": date,
        "morning": morning,
        "actual_market": actuals,
        "evaluation": evaluations,
        "user_action": user_action,
    }
    review, llm_status = call_llm(EVENING_SYSTEM_PROMPT, llm_payload, config)
    if not isinstance(review, dict):
        review = {
            "summary": "LLM 복기를 사용할 수 없어 정량 비교만 저장했습니다.",
            "good_judgments": [f"{x['instrument']}: direction hit" for x in evaluations if x["direction_hit"]],
            "wrong_judgments": [f"{x['instrument']}: {', '.join(x['error_tags'])}" for x in evaluations if x["error_tags"]],
            "error_candidates": sorted({tag for x in evaluations for tag in x["error_tags"]}),
            "next_adjustments": ["누적 표본에서 방향·범위 적중률을 계속 측정한다."],
            "principle_review": "사용자 행동이 명시되지 않았으면 원칙 준수 여부를 평가하지 않는다.",
        }
    return {
        "generated_at": now_kst().isoformat(timespec="seconds"),
        "analysis_date": date,
        "status": "ok",
        "actual_market": actuals,
        "evaluation": evaluations,
        "user_action": user_action,
        "llm_status": llm_status,
        "review": review,
    }


def aggregate_performance(records: list[dict[str, Any]]) -> dict[str, Any]:
    evaluations = []
    principle_flags = []
    by_action: dict[str, list[float]] = {}
    error_counts: dict[str, int] = {}
    for record in records:
        evening = record.get("evening") or {}
        for e in evening.get("evaluation", []):
            evaluations.append(e)
            action = e.get("morning_strategy") or "UNKNOWN"
            by_action.setdefault(action, []).append(float(e["actual_close_return"]))
            for tag in e.get("error_tags", []):
                error_counts[tag] = error_counts.get(tag, 0) + 1
        action = record.get("user_action")
        if isinstance(action, dict) and isinstance(action.get("principle_followed"), bool):
            principle_flags.append(bool(action["principle_followed"]))

    n = len(evaluations)
    return {
        "updated_at": now_kst().isoformat(timespec="seconds"),
        "samples": n,
        "direction_accuracy": (sum(bool(x["direction_hit"]) for x in evaluations) / n) if n else None,
        "range_accuracy": (sum(bool(x["range_hit"]) for x in evaluations) / n) if n else None,
        "close_in_range_accuracy": (sum(bool(x["close_in_range"]) for x in evaluations) / n) if n else None,
        "principle_compliance_rate": (sum(principle_flags) / len(principle_flags)) if principle_flags else None,
        "strategy_outcomes": {
            action: {
                "samples": len(values),
                "average_actual_close_return": statistics.fmean(values) if values else None,
                "positive_return_rate": sum(v > 0 for v in values) / len(values) if values else None,
            }
            for action, values in sorted(by_action.items())
        },
        "repeated_judgment_errors": dict(sorted(error_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "notes": [
            "Principle compliance is calculated only from explicitly recorded user_action.principle_followed values.",
            "No user trade is inferred from market movement.",
        ],
    }


def render_morning_markdown(date: str, morning: dict[str, Any]) -> str:
    lines = [
        "---",
        f'title: "{date} 투자 브리핑 및 복기"',
        f"date: {date}",
        "draft: false",
        f'description: "{date} 투자 오전 분석과 저녁 복기를 한 페이지에 누적한다."',
        'categories: ["Investment", "Log"]',
        'tags: ["Investment", "ETF", "Daily Briefing", "Automation"]',
        "---",
        "",
        "> 정보수집·분석·판단 보조 기록이다. 실제 주문을 자동 실행하지 않는다.",
        "",
        "## 오전 브리핑",
        "",
        f"- 분석 일자: {date}",
        f"- LLM 상태: `{morning.get('llm_status')}`",
        "",
        "### 기술적 분석과 익일 범위",
        "",
        "| 자산 | 기준가 | 예상 저가~고가 | 방향 | RSI14 | ATR14 | ADX14 |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for m in morning.get("market", []):
        if m.get("status") != "ok":
            lines.append(f"| {m.get('name')} | 오류 | - | - | - | - | - |")
            continue
        f = m["forecast"]
        ind = m["indicators"]
        lines.append(
            f"| {m['name']} | {money(m['current_price'])} | {money(f['predicted_range']['low'])}~{money(f['predicted_range']['high'])} | "
            f"{f['direction']} | {ind.get('rsi_14', 0):.1f} | {money(ind.get('atr_14'))} | {ind.get('adx_14', 0):.1f} |"
        )

    lines += ["", "### 예측 범위에 따른 이동평균·볼린저 예상 범위", ""]
    for m in morning.get("market", []):
        if m.get("status") != "ok":
            continue
        ranges = m.get("projected_indicator_ranges", {})
        parts = []
        for key in ("ma5", "ma10", "ma20", "ma60", "ma120", "bb_lower", "bb_mid", "bb_upper"):
            if key in ranges:
                lo, hi = ranges[key]
                parts.append(f"{key.upper()} {money(lo)}~{money(hi)}")
        lines.append(f"- **{m['name']}**: " + " · ".join(parts))

    macro = morning.get("macro", {})
    lines += ["", "### 거시경제", ""]
    if macro.get("indicators"):
        for item in macro["indicators"]:
            if item.get("status") == "ok":
                lines.append(f"- {item.get('name')}: {item.get('value')} ({item.get('date')})")
            else:
                lines.append(f"- {item.get('name')}: 수집 실패")
    else:
        lines.append(f"- 수집 상태: {macro.get('status')} — {macro.get('reason', '')}")

    news = morning.get("news", {})
    lines += ["", "### 주요 뉴스", ""]
    for article in news.get("articles", [])[:8]:
        title = (article.get("title") or "").replace("[", "(").replace("]", ")")
        source = article.get("source") or "source"
        url = article.get("url") or ""
        if url:
            lines.append(f"- [{title}]({url}) — {source}")
        else:
            lines.append(f"- {title} — {source}")
    if not news.get("articles"):
        lines.append(f"- 뉴스 수집 상태: {news.get('status')}")

    analysis = morning.get("llm_analysis", {})
    lines += [
        "",
        "### 종합 판단",
        "",
        analysis.get("market_summary", ""),
        "",
        f"**거시 상태:** {analysis.get('macro_state', '')}",
        "",
        "### 오늘의 실행 전략 후보",
        "",
    ]
    for s in analysis.get("strategies", []):
        lines += [
            f"- **{s['instrument']} — {s['action']}**",
            f"  - 근거: {s.get('reason', '')}",
            f"  - 무효화 조건: {s.get('invalidation', '')}",
            f"  - 위험: {'; '.join(s.get('risks', []))}",
        ]
    study = analysis.get("study", {})
    lines += [
        "",
        "### 경제 공부 한 꼭지",
        "",
        f"**{study.get('concept', '')}** — {study.get('explanation', '')}",
        "",
        "### 불확실성",
        "",
    ]
    for x in analysis.get("uncertainty", []):
        lines.append(f"- {x}")
    lines += [
        "- Colab의 pooled LSTM A/B는 현재 저장소에 학습 워크북·체크포인트가 없어 아직 동일 재현하지 않는다. 현재 범위는 누수 없는 과거 익일 OHLC 경험 분위수 기준선이다.",
        "",
    ]
    return "\n".join(lines)


def append_evening_markdown(markdown: str, evening: dict[str, Any], performance: dict[str, Any]) -> str:
    if "\n## 저녁 복기\n" in markdown:
        markdown = markdown.split("\n## 저녁 복기\n", 1)[0].rstrip() + "\n"
    lines = [
        "",
        "## 저녁 복기",
        "",
        f"- 상태: `{evening.get('status')}`",
    ]
    if evening.get("status") != "ok":
        lines.append(f"- 사유: {evening.get('reason', '')}")
        return markdown.rstrip() + "\n" + "\n".join(lines) + "\n"

    lines += [
        "",
        "### 오전 예상 vs 실제",
        "",
        "| 자산 | 오전 방향 | 실제 방향 | 방향 적중 | 범위 적중 | 실제 종가수익률 |",
        "|---|---|---|---|---|---:|",
    ]
    for e in evening.get("evaluation", []):
        lines.append(
            f"| {e['instrument']} | {e['predicted_direction']} | {e['actual_direction']} | "
            f"{'O' if e['direction_hit'] else 'X'} | {'O' if e['range_hit'] else 'X'} | {pct(e['actual_close_return'])} |"
        )

    action = evening.get("user_action")
    lines += ["", "### 사용자 실제 행동", ""]
    if isinstance(action, dict):
        lines.append(f"- 명시 기록: {json.dumps(action, ensure_ascii=False)}")
    else:
        lines.append("- 기록 없음. 자동화는 사용자의 매수·매도·보유·관망을 추정하지 않는다.")

    review = evening.get("review", {})
    lines += ["", "### 복기", "", review.get("summary", "")]
    for title, key in [
        ("잘된 판단", "good_judgments"),
        ("틀린 판단", "wrong_judgments"),
        ("오류 원인 후보", "error_candidates"),
        ("다음 분석 반영", "next_adjustments"),
    ]:
        lines += ["", f"**{title}**"]
        vals = review.get(key, [])
        if vals:
            lines.extend(f"- {x}" for x in vals)
        else:
            lines.append("- 없음/판단 불가")
    lines += [
        "",
        f"**원칙 준수 검토:** {review.get('principle_review', '')}",
        "",
        "### 누적 성과",
        "",
        f"- 방향 예측 적중률: {pct(performance.get('direction_accuracy'))}",
        f"- 가격 범위 적중률: {pct(performance.get('range_accuracy'))}",
        f"- 종가 범위 적중률: {pct(performance.get('close_in_range_accuracy'))}",
        f"- 원칙 준수율: {pct(performance.get('principle_compliance_rate'))}",
        f"- 누적 평가 표본: {performance.get('samples', 0)}",
        f"- 반복 오류: {json.dumps(performance.get('repeated_judgment_errors', {}), ensure_ascii=False)}",
        "",
    ]
    return markdown.rstrip() + "\n" + "\n".join(lines) + "\n"


def run(cycle: str, date: str | None) -> None:
    config = read_json(CONFIG_PATH, {})
    if not config:
        raise RuntimeError(f"missing config: {CONFIG_PATH}")
    analysis_date = date or now_kst().date().isoformat()
    records = read_json(DAILY_PATH, [])
    if not isinstance(records, list):
        raise ValueError("data/investment_daily.json must be a JSON array")
    record = find_daily(records, analysis_date) or {"date": analysis_date, "user_action": None}

    daily_dir = LOG_ROOT / analysis_date
    markdown_path = daily_dir / "index.md"
    if cycle == "morning":
        morning = morning_cycle(config, analysis_date)
        record["morning"] = morning
        records = upsert_daily(records, record)
        atomic_write_json(DAILY_PATH, records)
        performance = aggregate_performance(records)
        atomic_write_json(PERFORMANCE_PATH, performance)
        daily_dir.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_morning_markdown(analysis_date, morning), encoding="utf-8")
        ok_count = sum(x.get("status") == "ok" for x in morning["market"])
        print(f"Morning investment analysis complete: {ok_count}/{len(morning['market'])} market instruments collected.")
        return

    if cycle == "evening":
        evening = evening_cycle(config, analysis_date, record)
        record["evening"] = evening
        records = upsert_daily(records, record)
        atomic_write_json(DAILY_PATH, records)
        performance = aggregate_performance(records)
        atomic_write_json(PERFORMANCE_PATH, performance)
        daily_dir.mkdir(parents=True, exist_ok=True)
        if markdown_path.exists():
            markdown = markdown_path.read_text(encoding="utf-8")
        elif record.get("morning"):
            markdown = render_morning_markdown(analysis_date, record["morning"])
        else:
            markdown = (
                "---\n"
                f'title: "{analysis_date} 투자 브리핑 및 복기"\n'
                f"date: {analysis_date}\n"
                "draft: false\n"
                f'description: "{analysis_date} 투자 자동화 실행 기록."\n'
                'categories: ["Investment", "Log"]\n'
                'tags: ["Investment", "ETF", "Automation"]\n'
                "---\n"
            )
        markdown_path.write_text(append_evening_markdown(markdown, evening, performance), encoding="utf-8")
        print(f"Evening investment review complete: {len(evening.get('evaluation', []))} instrument evaluations.")
        return

    raise ValueError(f"unsupported cycle: {cycle}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", choices=("morning", "evening"), required=True)
    parser.add_argument("--date", help="Override KST analysis date (YYYY-MM-DD), mainly for manual recovery.")
    args = parser.parse_args()
    run(args.cycle, args.date)


if __name__ == "__main__":
    main()
