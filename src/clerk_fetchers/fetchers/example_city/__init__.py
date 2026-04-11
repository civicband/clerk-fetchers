from typing import Any, Literal, override


import json

from bs4 import BeautifulSoup
from clerk import Fetcher


class ExampleCityFetcher(Fetcher):
    """Example fetcher demonstrating how to build a clerk-fetchers plugin.

    This fetcher scrapes meeting minutes from a hypothetical city government
    website. Use it as a template for building your own fetcher.
    """

    @override
    def child_init(self):
        extra: dict[Any, Any] = self.site.get("extra", "{}")
        if isinstance(extra, str):
            extra = json.loads(extra)
        self.base_url: Any = extra.get("base_url", "https://example-city.gov/meetings")  # pyright: ignore[reportUninitializedInstanceVariable]

    @override
    def fetch_events(self) -> tuple[Any, Any]:  # pyright: ignore[reportIncompatibleMethodOverride]
        resp: Any = self.request("GET", self.base_url)
        soup: Any = BeautifulSoup(resp.text, "html.parser")

        rows: Any = soup.select("tr.meeting-row")
        for row in rows:
            link: Any = row.select_one("a.minutes-link")
            if not link:
                continue

            title: Any = row.select_one("td.meeting-title")
            meeting_name: Any | Literal["Unknown Meeting"] = (
                title.get_text(strip=True) if title else "Unknown Meeting"
            )

            date_cell: Any = row.select_one("td.meeting-date")
            date_text: Any | Literal[""] = (
                date_cell.get_text(strip=True) if date_cell else ""
            )

            href: Any = link.get("href", "")
            if href and not href.startswith("http"):
                href = f"{self.base_url.rstrip('/')}/{href.lstrip('/')}"

            if href and href.endswith(".pdf"):
                self.fetch_and_write_pdf(
                    href,
                    self.minutes_output_dir,
                    self.simplified_meeting_name(meeting_name),
                    date_text,
                )
                self.total_minutes += 1

            self.total_events += 1

        return self.total_events, self.total_minutes
