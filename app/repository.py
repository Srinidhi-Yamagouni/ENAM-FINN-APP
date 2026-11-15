"""Data access. Live snapshots override the bundled fallback data per dataset."""
import json
import os
import datetime as dt
from functools import lru_cache
from . import fixtures

# Separate namespace prevents data from the earlier prototype being mistaken for
# a live source in this independent submission.
LIVE = os.path.join(os.path.dirname(__file__), "..", "data", "current")


def _live(name):
    p = os.path.join(LIVE, name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None


def now():
    return dt.datetime.now(dt.timezone.utc)


@lru_cache(maxsize=1)
def companies():
    return [dict(ticker=t, name=n, sector=s, cap=c, weight=w, aliases=a) for t, n, s, c, w, _, a in fixtures.COMPANIES]


def company(ticker):
    return next((c for c in companies() if c["ticker"] == ticker.upper()), None)


def relations(ticker):
    return fixtures.RELATIONS.get(ticker.upper(), {"competitors": [], "suppliers": [], "customers": []})


@lru_cache(maxsize=1)
def prices():
    base = fixtures.gen_prices()
    live = _live("prices.json") or {}
    ok = lambda r: isinstance(r.get("c"), (int, float)) and r["c"] == r["c"] and r["c"] > 0   # NaN != NaN
    live = {t: [r for r in v if ok(r)] for t, v in live.items()}
    base.update({t: v for t, v in live.items() if len(v) > 25})   # live data wins per ticker; empty live series fall back to fixtures
    return base


def live_layers():
    """Which layers are running on real data (for the UI badge)."""
    ann = bool(_live("announcements.json"))
    px = any(v for v in (_live("prices.json") or {}).values())
    fund = sorted(f[13:-5] for f in (os.listdir(LIVE) if os.path.isdir(LIVE) else []) if f.startswith("fundamentals_") and f.endswith(".json"))
    current = {c["ticker"] for c in companies()}
    if ann:
        ann = any(item.get("ticker") in current for item in (_live("announcements.json") or []))
    fund = [ticker for ticker in fund if ticker in current]
    px = any(ticker in current and values for ticker, values in (_live("prices.json") or {}).items())
    return dict(prices=px, announcements=ann, fundamentals=fund)


def announcements():
    live = _live("announcements.json")
    if live and any(company(item.get("ticker", "")) for item in live):
        return live
    n = now()
    return [dict(id=i, ticker=t, ts=(n - dt.timedelta(hours=h)).isoformat(), subject=s, body=b, person=p)
            for i, t, h, s, b, p in fixtures.ANNOUNCEMENTS]


@lru_cache(maxsize=1)
def people():
    return _live("people.json") or [dict(p, edu=[dict(school=a, year=b) for a, b in p["edu"]]) for p in fixtures.PEOPLE]


@lru_cache(maxsize=1)
def ext_people():
    return _live("ext_people.json") or [dict(p, edu=[dict(school=a, year=b) for a, b in p["edu"]]) for p in fixtures.EXT_PEOPLE]


def fundamentals(ticker):
    t = ticker.upper()
    live = _live(f"fundamentals_{t}.json")
    if live:
        return live
    return fixtures.FUNDAMENTALS.get(t)
