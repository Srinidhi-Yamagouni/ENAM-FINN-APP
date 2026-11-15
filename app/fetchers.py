"""Opt-in live fetchers for the v2 universe.

The demo never calls these during startup. They are rate-limited, cached, and
return a provenance record so a failed refresh cannot masquerade as live data.
"""
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from . import repository

CURRENT = Path(__file__).resolve().parents[1] / "data" / "current"
CACHE = Path(__file__).resolve().parents[1] / "snapshot_cache"
NSE = "https://www.nseindia.com/api/corporate-announcements?index=equities&symbol="


def _request(url: str, timeout: float = 4.0, retries: int = 1):
    headers = {
        "User-Agent": "FINN research prototype/1.0 (respectful demo)",
        "Accept": "application/json,text/html",
    }
    for attempt in range(retries + 1):
        try:
            with urlopen(Request(url, headers=headers), timeout=timeout) as response:
                return response.read(), response.headers.get_content_type()
        except Exception:
            if attempt < retries:
                time.sleep(0.5 * (2**attempt))
    return None, None


def _write(name: str, payload):
    CURRENT.mkdir(parents=True, exist_ok=True)
    target = CURRENT / name
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False))
    temp.replace(target)


def fetch_prices():
    """Fetch EOD close/volume for every current portfolio symbol with yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        return {"source": "fallback", "reason": "yfinance is not installed", "tickers": []}
    output = {}
    for company in repository.companies():
        symbol = f"{company['ticker']}.NS"
        try:
            frame = yf.download(symbol, period="6mo", interval="1d", progress=False, timeout=10)
            rows = []
            if frame is not None and not frame.empty:
                for index, row in frame.iterrows():
                    close = row.get("Close")
                    volume = row.get("Volume")
                    if hasattr(close, "iloc"):
                        close = close.iloc[0]
                    if hasattr(volume, "iloc"):
                        volume = volume.iloc[0]
                    if close == close and volume == volume:
                        rows.append({"d": index.strftime("%Y-%m-%d"), "c": float(close), "v": int(volume)})
            if rows:
                output[company["ticker"]] = rows
        except Exception:
            continue
        time.sleep(0.2)
    if output:
        _write("prices.json", output)
        return {"source": "live", "tickers": sorted(output)}
    return {"source": "fallback", "reason": "no symbols returned", "tickers": []}


def fetch_announcements(limit_per_ticker: int = 20):
    """Fetch public NSE announcement JSON; malformed or blocked responses are skipped."""
    def one(company):
        output = []
        body, content_type = _request(NSE + quote(company["ticker"]))
        if not body or "json" not in (content_type or ""):
            return output
        try:
            rows = json.loads(body)
        except json.JSONDecodeError:
            return output
        for row in rows[:limit_per_ticker]:
            output.append({
                "id": hashlib.sha1(f'{company["ticker"]}:{row}'.encode()).hexdigest()[:12],
                "ticker": company["ticker"],
                "ts": row.get("an_dt") or row.get("date"),
                "subject": row.get("attchmntText") or row.get("subject") or "Exchange announcement",
                "body": row.get("attchmntText") or "",
                "person": None,
            })
        return output

    output = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(one, company) for company in repository.companies()]
        for future in as_completed(futures):
            output.extend(future.result())
    if output:
        _write("announcements.json", output)
        return {"source": "live", "count": len(output)}
    return {"source": "fallback", "count": 0}


def cache_document(url: str):
    """Cache a primary annual-report/transcript URL by content hash."""
    body, content_type = _request(url, timeout=15, retries=2)
    if not body:
        return {"source": "fallback", "url": url}
    digest = hashlib.sha256(body).hexdigest()
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{digest}.bin"
    if not path.exists():
        path.write_bytes(body)
    return {"source": "live", "url": url, "content_hash": digest, "content_type": content_type}


def refresh():
    """Run the bounded refresh manually; startup stays fully offline."""
    return {"prices": fetch_prices(), "announcements": fetch_announcements()}
