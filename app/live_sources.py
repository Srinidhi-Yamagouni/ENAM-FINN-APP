"""Polite optional live adapters with timeout, retry, and snapshot fallback."""
import hashlib
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

from . import repository

CACHE = Path(__file__).resolve().parents[1] / "snapshot_cache"


def _cache_path(url: str) -> Path:
    return CACHE / f"{hashlib.sha256(url.encode()).hexdigest()}.json"


def fetch_json(url: str, timeout: float = 8.0, retries: int = 2) -> tuple[dict | list | None, str]:
    """Fetch once per attempt; report live or snapshot rather than hiding provenance."""
    CACHE.mkdir(exist_ok=True)
    path = _cache_path(url)
    for attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "FINN prototype contact@example.invalid"})
            with urlopen(request, timeout=timeout) as response:
                body = response.read()
            payload = json.loads(body)
            path.write_text(json.dumps({"fetched_at": time.time(), "payload": payload}))
            return payload, "live"
        except Exception:
            if attempt < retries:
                time.sleep(0.25 * (2 ** attempt))
    if path.exists():
        return json.loads(path.read_text())["payload"], "snapshot"
    return None, "bundled snapshot"


def portfolio_prices() -> tuple[dict, str]:
    """Use yfinance when installed; never make startup depend on a network call."""
    try:
        import yfinance as yf
        tickers = " ".join(f"{c['ticker']}.NS" for c in repository.companies())
        frame = yf.download(tickers, period="3mo", interval="1d", progress=False, timeout=8, group_by="ticker")
        if frame is not None and not frame.empty:
            return {"rows": int(len(frame))}, "live"
    except Exception:
        pass
    return repository.prices(), "bundled snapshot"
