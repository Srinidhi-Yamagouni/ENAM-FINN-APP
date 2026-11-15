import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from . import fetchers, model_runtime, relationship_graph, services, repository

app = FastAPI(title="FINN")
STATIC = os.path.join(os.path.dirname(__file__), "..", "static")


@app.get("/api/meta")
def meta():
    return services.investor.meta()


@app.get("/api/llm")
def llm_status():
    """Open this in a browser to see whether model calls are really happening."""
    return dict(provider=model_runtime.provider(), model=model_runtime.model_name(), **model_runtime.STATS)


@app.get("/api/digest")
def digest(hours: int = Query(24, ge=1, le=720), cats: Optional[str] = None):
    return services.investor.dashboard(hours, cats, 2.0, 4.0)["digest"]


@app.get("/api/alerts")
def alerts(vol_x: float = 2.0, px: float = 4.0):
    return services.investor.dashboard(24, None, vol_x, px)["alerts"]


@app.get("/api/dashboard")
def dashboard(
    hours: int = Query(24, ge=1, le=720),
    cats: Optional[str] = None,
    vol_x: float = 2.0,
    px: float = 4.0,
):
    return services.investor.dashboard(hours, cats, vol_x, px)


@app.post("/api/refresh")
def refresh():
    return fetchers.refresh()


@app.get("/api/research/{ticker}")
def research(ticker: str):
    try:
        r = services.investor.research(ticker)
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not r:
        raise HTTPException(404, f"No fundamentals for {ticker}.")
    return r


@app.get("/api/network/graph/{ticker}")
def graph(ticker: str):
    if not repository.company(ticker):
        raise HTTPException(404, "Unknown ticker")
    return services.investor.graph(ticker)


@app.get("/api/network/expertise")
def expertise(theme: str):
    return services.investor.expertise(theme)


@app.get("/api/network/people")
def people():
    return services.investor.directory()


@app.get("/api/network/person/{pid}")
def person(pid: str):
    d = services.investor.person(pid)
    if not d:
        raise HTTPException(404, "Unknown person")
    return d


@app.get("/api/network/warm")
def warm():
    return services.investor.warm()


class Q(BaseModel):
    q: str


@app.post("/api/ask")
def ask(body: Q):
    try:
        return services.investor.ask(body.q)
    except RuntimeError as e:
        raise HTTPException(503, str(e)) from e


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC), name="static")
