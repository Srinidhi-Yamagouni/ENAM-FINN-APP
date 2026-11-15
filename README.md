# FINN

FINN is a mobile-first investment intelligence prototype with three woven workflows:

- **Push**: a configurable time-window digest, unusual price/volume alerts, results treatment,
  management-change enrichment, and a network-recommended person to call.
- **Pull**: primary-document research with trajectory, balance sheet, cash quality, and
  narrative-vs-numbers output.
- **Network**: who-to-call, second-degree reach, people diligence, expertise mapping, and
  keep-warm prompts.

This is the second, independent submission. It has its own module structure and data model.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. The bundled snapshot makes the demo work offline.

Docker:

```bash
docker build -t finn .
docker run --rm -p 8000:8000 finn
```

## Built versus proposed

**Built:** FastAPI API, mobile static client, digest and configurable alerts, results
comparison, primary-source research cards, evidence verification helper, network
recommendations and second-degree graph, offline snapshot fallback, optional Hyde model
configuration, and focused automated tests.

**Proposed next:** production exchange adapters, PDF page-level extraction for arbitrary
unseen tickers, authenticated tenant isolation, encrypted contact storage, background
refresh workers, and a stronger model verification pass. The prototype never presents
the bundled data as live.

## Data pipeline and freshness

The bundled `data/live/` files are clearly treated as snapshot inputs. `repository.py`
normalises them and the API exposes which layers are live versus snapshot. `live_sources.py`
contains a timeout/retry/backoff adapter with URL-hash disk caching. The optional yfinance
adapter fetches NSE `.NS` symbols; if it fails, the app continues with the bundled data.
Production would add a rate-limited NSE/BSE announcement client and an investor-relations
document queue. Every cached payload needs a fetched timestamp before it is labelled live.

Announcements are classified using the glossary categories. Results rows are parsed into
Revenue, EBITDA, PBT and PAT and compared QoQ/YoY. Management names are matched to network
profiles through normalised names and employer history, then scored with relationship
strength, recency and sector relevance.

## Evidence and model behaviour

The research engine computes numeric comparisons in Python. `evidence.py` checks that every
numeric claim occurs in its cited source span; mismatches are dropped rather than softened.
The configured Hyde model is optional. With no key, deterministic extraction and cached
research remain available and the UI reports offline mode. A production extraction worker
would chunk annual reports and transcripts, validate Pydantic JSON, retry malformed output,
and cache extraction by content hash. Cheap extraction handles volume; a stronger model is
reserved for narrative-vs-numbers reasoning.

The Ask endpoint is an application tool surface: the assistant can use digest, alerts,
research, who-to-call and diligence functions. The current offline path keeps the step
limit and deterministic tool results; model planning is proposed for the next worker.

## Network privacy

All people in this repository are realistic synthetic profiles. No LinkedIn or other
professional platform was scraped. A real deployment would ingest only consented exports
or user-provided CRM data, store the minimum fields (name, role, employer history, themes,
relationship strength and last-contact date), encrypt it per tenant, retain it for the
account lifetime plus a short deletion window, and enforce tenant-scoped access tokens.
Network data must never be sent to a model provider without explicit consent and redaction.

## Architecture

```text
FastAPI
  ├── services.py       API orchestration
  ├── repository.py     snapshot/live normalisation
  ├── digest.py         classification, scoring, alerts
  ├── research.py       primary-document analysis
  ├── relationship_graph.py  people links and recommendations
  ├── assistant.py      grounded Ask workflow
  ├── model_runtime.py  optional provider and cost counters
  └── live_sources.py   polite adapters and cache fallback
       └── static/index.html + app.js + style.css
```

## Original insight

FINN surfaces **context debt**: a material filing is ranked higher when the best relevant
contact has not been spoken to recently, because the cost of waiting is often greater than
the cost of a warm reconnect. This is separate from simple contact recency.

## Deliberate omissions

There is no broker execution, investment advice, scraped personal data, hidden live-data
claim, or full production PDF crawler. Those boundaries keep the demo safe and explainable.

## Tests

```bash
pytest -q
python3 -m py_compile app/*.py
node --check static/app.js
```
