"""Application services for the FINN desk API."""
from typing import Optional

from . import model_runtime, relationship_graph, research, digest, assistant, fixtures, repository


class InvestorService:
    """Keep API orchestration separate from the underlying data logic."""

    def meta(self):
        layers = repository.live_layers()
        synthetic = [
            name for name, available in
            (("prices", layers["prices"]), ("filings", layers["announcements"]))
            if not available
        ] + ["relationship_graph"]
        return {
            "synthetic": True,
            "synthetic_layers": synthetic,
            "live_fundamentals": layers["fundamentals"],
            "portfolio": repository.companies(),
            "themes": fixtures.THEMES,
            "categories": sorted(digest.BASE),
            "labels": digest.LABEL,
            "research_ready": sorted(fixtures.FUNDAMENTALS),
            "model_runtime": model_runtime.provider(),
            "freshness": {
                "prices": "live" if layers["prices"] else "snapshot",
                "announcements": "live" if layers["announcements"] else "snapshot",
                "fundamentals": "live" if layers["fundamentals"] else "snapshot",
                "network": "synthetic",
            },
        }

    def dashboard(self, hours: int, cats: Optional[str], vol_x: float, px: float):
        return {
            "digest": digest.digest(hours, cats.split(",") if cats else None),
            "alerts": digest.alerts(vol_x, px),
        }

    def research(self, ticker: str):
        return research.analyse(ticker)

    def graph(self, ticker: str):
        return relationship_graph.graph(ticker.upper())

    def expertise(self, theme: str):
        return relationship_graph.expertise(theme)

    def directory(self):
        return relationship_graph.directory()

    def person(self, pid: str):
        return relationship_graph.diligence(pid)

    def warm(self):
        return relationship_graph.keep_warm(repository.announcements())

    def ask(self, question: str):
        return assistant.ask(question)


investor = InvestorService()
