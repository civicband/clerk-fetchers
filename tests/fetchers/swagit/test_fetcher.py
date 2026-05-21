from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
import respx

from clerk_fetchers.fetchers.swagit import SwagitFetcher

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ARCHIVE_URL = (
    "https://uplandca.new.swagit.com/views/299/"
    "city-council-archived-meetings"
)


def make_site(extra=None):
    return {
        "subdomain": "upland.ca",
        "start_year": 2025,
        "pages": 0,
        "extra": extra or '{"swagit_subdomain": "uplandca", "view_id": "299"}',
    }


@pytest.fixture
def fetcher(tmp_path):
    with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
        return SwagitFetcher(make_site())


class TestSwagitFetcher:
    def test_child_init_parses_extra(self, fetcher):
        assert fetcher.swagit_subdomain == "uplandca"
        assert fetcher.view_id == "299"
        assert fetcher.base_url == "https://uplandca.new.swagit.com"
        assert fetcher.archive_path == "city-council-archived-meetings"

    def test_child_init_accepts_dict_extra(self, tmp_path):
        with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
            site = make_site(extra={"swagit_subdomain": "torranceca", "view_id": "1"})
            f = SwagitFetcher(site)
            assert f.swagit_subdomain == "torranceca"
            assert f.view_id == "1"

    def test_child_init_custom_archive_path(self, tmp_path):
        with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
            site = make_site(
                extra='{"swagit_subdomain": "x", "view_id": "1", '
                '"archive_path": "planning-archived-meetings"}'
            )
            f = SwagitFetcher(site)
            assert f.archive_path == "planning-archived-meetings"

    @respx.mock
    def test_fetch_events_paginates_and_stops_on_empty(self, fetcher):
        archive_html = (FIXTURES_DIR / "upland_archive_page1.html").read_text()
        empty_html = (FIXTURES_DIR / "upland_archive_empty.html").read_text()
        meeting_html = (FIXTURES_DIR / "upland_meeting_387382.html").read_text()

        respx.get(f"{ARCHIVE_URL}?page=1").mock(
            return_value=httpx.Response(200, text=archive_html)
        )
        respx.get(f"{ARCHIVE_URL}?page=2").mock(
            return_value=httpx.Response(200, text=empty_html)
        )
        respx.get(url__regex=r"https://uplandca\.new\.swagit\.com/videos/\d+").mock(
            return_value=httpx.Response(200, text=meeting_html)
        )

        fetcher.fetch_and_write_pdf = MagicMock()
        total_events, total_minutes = fetcher.fetch_events()

        assert total_events > 0
        assert total_minutes > 0
        assert fetcher.fetch_and_write_pdf.call_count == total_minutes

    def test_extract_agenda_pdf_url_finds_real_url(self, fetcher):
        html = (FIXTURES_DIR / "upland_meeting_387382.html").read_text()
        url = fetcher._extract_agenda_pdf_url(html)
        assert url is not None
        assert url.startswith(
            "https://swagit-attachments.granicus.com/uploads/video/agenda_file/"
        )
        assert url.endswith(".pdf")

    def test_extract_agenda_pdf_url_returns_none_when_missing(self, fetcher):
        assert fetcher._extract_agenda_pdf_url("<html></html>") is None

    def test_normalize_date_formats_iso(self, fetcher):
        assert fetcher._normalize_date("May 18, 2026") == "2026-05-18"

    def test_normalize_date_passthrough_on_unparseable(self, fetcher):
        raw = "not a date"
        assert fetcher._normalize_date(raw) == raw


class TestRegistry:
    def test_fetcher_registry_has_upland(self):
        from clerk_fetchers._registry import FETCHER_REGISTRY
        assert FETCHER_REGISTRY["upland.ca"] is SwagitFetcher

    def test_extra_registry_has_upland(self):
        from clerk_fetchers._registry import EXTRA_REGISTRY
        upland = EXTRA_REGISTRY["upland.ca"]
        assert upland["swagit_subdomain"] == "uplandca"
        assert upland["view_id"] == "299"


class TestPlugin:
    def test_fetcher_class_returns_swagit_for_upland(self):
        from clerk_fetchers import ClerkFetchersPlugin
        assert ClerkFetchersPlugin().fetcher_class(label="upland.ca") is SwagitFetcher

    def test_fetcher_extra_returns_upland_config(self):
        from clerk_fetchers import ClerkFetchersPlugin
        extra = ClerkFetchersPlugin().fetcher_extra(label="upland.ca")
        assert extra == {"swagit_subdomain": "uplandca", "view_id": "299"}
