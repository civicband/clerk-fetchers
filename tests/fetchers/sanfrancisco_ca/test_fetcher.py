from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from clerk_fetchers.fetchers.sanfrancisco_ca import (
    DEFAULT_CALENDAR_URL,
    YEAR_CLIENT_STATE,
    YEAR_EVENT_TARGET,
    SanFranciscoCAFetcher,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def make_site(extra=None):
    return {
        "subdomain": "sanfrancisco.ca",
        "start_year": 2025,
        "pages": 0,
        "extra": extra or "{}",
    }


@pytest.fixture
def fetcher(tmp_path):
    with patch("clerk.fetcher.STORAGE_DIR", str(tmp_path)):
        return SanFranciscoCAFetcher(make_site())


def response(name, cookies=None):
    return httpx.Response(
        200,
        text=(FIXTURES_DIR / name).read_text(),
        headers={"set-cookie": "session=abc"} if cookies else None,
        request=httpx.Request("GET", DEFAULT_CALENDAR_URL),
    )


class TestSanFranciscoCAFetcher:
    def test_child_init_defaults_calendar_url(self, fetcher):
        assert fetcher.calendar_url == DEFAULT_CALENDAR_URL

    def test_fetch_events_posts_year_paginates_and_downloads(self, fetcher):
        fetcher.today = datetime(2025, 7, 1, tzinfo=UTC)
        fetcher.all_agendas = True
        fetcher.request = MagicMock(
            side_effect=[
                response("calendar.html", {"session": "abc"}),
                response("year_page_1.html"),
                response("year_page_2.html"),
            ]
        )
        fetcher.fetch_and_write_pdf = MagicMock()

        assert fetcher.fetch_events() == (2, 2)
        assert fetcher.fetch_and_write_pdf.call_count == 4

        year_post = fetcher.request.call_args_list[1]
        assert year_post.args[:2] == ("POST", DEFAULT_CALENDAR_URL)
        assert year_post.kwargs["data"]["__EVENTTARGET"] == YEAR_EVENT_TARGET
        assert year_post.kwargs["data"][YEAR_CLIENT_STATE] == '{"value": "2025"}'
        assert year_post.kwargs["cookies"] == {"session": "abc"}

        page_post = fetcher.request.call_args_list[2]
        assert page_post.kwargs["data"]["__EVENTTARGET"] == "page-two"
        assert page_post.kwargs["data"]["__VIEWSTATE"] == "page-one-state"

        first_download = fetcher.fetch_and_write_pdf.call_args_list[0]
        assert first_download.args[:4] == (
            "https://sfgov.legistar.com/View.ashx?M=M&ID=10&GUID=m",
            "minutes",
            "BoardofSupervisors",
            "2025-01-14",
        )
        assert (Path(fetcher.minutes_output_dir) / "BoardofSupervisors").is_dir()
        assert (Path(fetcher.agendas_output_dir) / "BoardofSupervisors").is_dir()

    def test_row_with_unparseable_date_is_skipped(self, fetcher):
        fetcher.all_agendas = True
        fetcher.fetch_and_write_pdf = MagicMock()

        from bs4 import BeautifulSoup

        html = (FIXTURES_DIR / "year_page_1.html").read_text()
        page = BeautifulSoup(html.replace("1/14/2025", "Deferred"), "html.parser")
        assert fetcher._process_page(page) == (0, 0)
        fetcher.fetch_and_write_pdf.assert_not_called()

    def test_existing_document_is_not_downloaded(self, fetcher):
        fetcher.all_agendas = True
        fetcher.check_if_exists = MagicMock(return_value=True)
        fetcher.fetch_and_write_pdf = MagicMock()

        from bs4 import BeautifulSoup

        page = BeautifulSoup(
            (FIXTURES_DIR / "year_page_1.html").read_text(), "html.parser"
        )
        assert fetcher._process_page(page) == (1, 0)
        fetcher.fetch_and_write_pdf.assert_not_called()


class TestRegistry:
    def test_registry_has_san_francisco_configuration(self):
        from clerk_fetchers._registry import EXTRA_REGISTRY, FETCHER_REGISTRY

        assert FETCHER_REGISTRY["sanfrancisco.ca"] is SanFranciscoCAFetcher
        assert EXTRA_REGISTRY["sanfrancisco.ca"]["calendar_url"] == DEFAULT_CALENDAR_URL
