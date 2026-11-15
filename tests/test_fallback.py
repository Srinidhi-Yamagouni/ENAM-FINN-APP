from app import live_sources, repository


def test_missing_live_source_reports_bundled_fallback():
    payload, source = live_sources.fetch_json("http://127.0.0.1:9/unavailable", retries=0)
    assert payload is None
    assert source == "bundled snapshot"


def test_new_research_ticker_uses_local_fallback():
    result = repository.fundamentals("MOTHERSON")
    assert result is not None
    assert result["name"] == "Samvardhana Motherson"
