from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
import respx

from clerk_fetchers.fetchers.example_city import ExampleCityFetcher

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def make_site(extra=None):
    return {
        "subdomain": "example-city.test",
        "start_year": 2025,
        "pages": 0,
        "extra": extra or '{"base_url": "https://example-city.gov/meetings"}',
    }


@pytest.fixture
def fetcher(tmp_path):
    with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
        site = make_site()
        f = ExampleCityFetcher(site)
        return f


class TestExampleCityFetcher:
    def test_child_init_parses_extra(self, fetcher):
        assert fetcher.base_url == "https://example-city.gov/meetings"

    def test_child_init_default_base_url(self, tmp_path):
        with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
            site = make_site(extra="{}")
            f = ExampleCityFetcher(site)
            assert f.base_url == "https://example-city.gov/meetings"

    @respx.mock
    def test_fetch_events_parses_meetings(self, fetcher):
        html = (FIXTURES_DIR / "meetings_page.html").read_text()
        respx.get("https://example-city.gov/meetings").mock(
            return_value=httpx.Response(200, text=html)
        )
        # Mock fetch_and_write_pdf to avoid actual file downloads
        fetcher.fetch_and_write_pdf = MagicMock()

        total_events, total_minutes = fetcher.fetch_events()

        assert total_events == 2
        assert total_minutes == 2
        assert fetcher.fetch_and_write_pdf.call_count == 2

    @respx.mock
    def test_fetch_events_relative_url(self, fetcher):
        html = (FIXTURES_DIR / "meetings_page.html").read_text()
        respx.get("https://example-city.gov/meetings").mock(
            return_value=httpx.Response(200, text=html)
        )
        fetcher.fetch_and_write_pdf = MagicMock()

        fetcher.fetch_events()

        # First call should have the relative URL resolved
        first_call_url = fetcher.fetch_and_write_pdf.call_args_list[0][0][0]
        assert first_call_url == "https://example-city.gov/meetings/files/minutes-2025-01-15.pdf"

    @respx.mock
    def test_fetch_events_absolute_url(self, fetcher):
        html = (FIXTURES_DIR / "meetings_page.html").read_text()
        respx.get("https://example-city.gov/meetings").mock(
            return_value=httpx.Response(200, text=html)
        )
        fetcher.fetch_and_write_pdf = MagicMock()

        fetcher.fetch_events()

        # Second call should keep the absolute URL
        second_call_url = fetcher.fetch_and_write_pdf.call_args_list[1][0][0]
        assert second_call_url == "https://example-city.gov/files/planning-2025-01-08.pdf"

    @respx.mock
    def test_fetch_events_skips_rows_without_link(self, fetcher):
        html = (FIXTURES_DIR / "meetings_page.html").read_text()
        respx.get("https://example-city.gov/meetings").mock(
            return_value=httpx.Response(200, text=html)
        )
        fetcher.fetch_and_write_pdf = MagicMock()

        total_events, total_minutes = fetcher.fetch_events()

        # Budget Committee row has no minutes link, so only 2 PDFs fetched
        # but all 3 rows with minutes-link or not are counted... actually
        # rows without a minutes-link are skipped entirely (continue)
        # so only 2 events counted
        assert total_events == 2


class TestRegistry:
    def test_fetcher_registry_has_example_city(self):
        from clerk_fetchers._registry import FETCHER_REGISTRY
        assert "example_city" in FETCHER_REGISTRY
        assert FETCHER_REGISTRY["example_city"] is ExampleCityFetcher

    def test_extra_registry_has_example_city(self):
        from clerk_fetchers._registry import EXTRA_REGISTRY
        assert "example_city" in EXTRA_REGISTRY
        assert "base_url" in EXTRA_REGISTRY["example_city"]


class TestPlugin:
    def test_fetcher_class_returns_class(self):
        from clerk_fetchers import ClerkFetchersPlugin
        plugin = ClerkFetchersPlugin()
        assert plugin.fetcher_class(label="example_city") is ExampleCityFetcher

    def test_fetcher_class_returns_none_for_unknown(self):
        from clerk_fetchers import ClerkFetchersPlugin
        plugin = ClerkFetchersPlugin()
        assert plugin.fetcher_class(label="nonexistent") is None

    def test_fetcher_extra_returns_config(self):
        from clerk_fetchers import ClerkFetchersPlugin
        plugin = ClerkFetchersPlugin()
        extra = plugin.fetcher_extra(label="example_city")
        assert extra == {"base_url": "https://example-city.gov/meetings"}

    def test_fetcher_extra_returns_none_for_unknown(self):
        from clerk_fetchers import ClerkFetchersPlugin
        plugin = ClerkFetchersPlugin()
        assert plugin.fetcher_extra(label="nonexistent") is None
