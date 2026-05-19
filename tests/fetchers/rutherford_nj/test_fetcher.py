from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import respx

from clerk_fetchers.fetchers.rutherford_nj import RutherfordNJFetcher

FIXTURES_DIR = Path(__file__).parent / "fixtures"
BASE_URL = "https://www.rutherfordboronj.com"


def make_site(start_year=2026):
    return {
        "subdomain": "rutherford.nj.civic.band",
        "start_year": start_year,
        "pages": 0,
        "extra": None,
    }


@respx.mock
def test_fetch_events_downloads_pdfs(tmp_path):
    with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
        f = RutherfordNJFetcher(make_site())

    respx.get(f"{BASE_URL}/meetings/meeting-documents/mayor-council-meeting").mock(
        return_value=httpx.Response(200, text=(FIXTURES_DIR / "top_level.html").read_text())
    )
    respx.get(url__regex=r".*2026-mayor-and-council-meeting-documents$").mock(
        return_value=httpx.Response(200, text=(FIXTURES_DIR / "year_2026.html").read_text())
    )
    respx.get(url__regex=r".*2026-minutes-mayor-council$").mock(
        return_value=httpx.Response(200, text=(FIXTURES_DIR / "minutes_2026.html").read_text())
    )
    respx.get(url__regex=r".*2026-agendas-mayor-council$").mock(
        return_value=httpx.Response(200, text="<html><body></body></html>")
    )

    f.fetch_and_write_pdf = MagicMock()
    f.fetch_events()

    assert f.fetch_and_write_pdf.call_count == 3
    first_call_args = f.fetch_and_write_pdf.call_args_list[0][0]
    assert first_call_args[1] == "minutes"
    assert first_call_args[2] == "MayorAndCouncil"
    assert first_call_args[3] == "2026-04-27"


def test_parse_date_standard(tmp_path):
    with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
        f = RutherfordNJFetcher(make_site())
    assert f._parse_date_from_slug("1291-04-27-2026-mayor-council-meeting-minutes") == "2026-04-27"


def test_parse_date_single_digit(tmp_path):
    with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
        f = RutherfordNJFetcher(make_site())
    assert f._parse_date_from_slug("986-8-25-2025-mayor-and-council-minutes") == "2025-08-25"


def test_parse_date_month_name(tmp_path):
    with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
        f = RutherfordNJFetcher(make_site())
    assert f._parse_date_from_slug("915-may-12-2025-minutes-pdf") == "2025-05-12"


def test_registry():
    from clerk_fetchers._registry import FETCHER_REGISTRY
    assert "rutherford.nj" in FETCHER_REGISTRY
    assert FETCHER_REGISTRY["rutherford.nj"] is RutherfordNJFetcher
