"""Fetcher for San Francisco's official Legistar meeting calendar."""

import json
import re
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Any, override
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from clerk import Fetcher

DEFAULT_CALENDAR_URL = "https://sfgov.legistar.com/Calendar.aspx"
YEAR_EVENT_TARGET = "ctl00$ContentPlaceHolder1$lstYears"
YEAR_CLIENT_STATE = "ctl00_ContentPlaceHolder1_lstYears_ClientState"
ROW_SELECTOR = (
    "#ctl00_ContentPlaceHolder1_gridCalendar tbody tr.rgRow, "
    "#ctl00_ContentPlaceHolder1_gridCalendar tbody tr.rgAltRow"
)


class SanFranciscoCAFetcher(Fetcher):
    """Fetch Board of Supervisors meetings directly from Legistar."""

    @override
    def child_init(self) -> None:
        extra: dict[str, Any] | str = self.site.get("extra", "{}")
        if isinstance(extra, str):
            extra = json.loads(extra)
        self.calendar_url = extra.get("calendar_url", DEFAULT_CALENDAR_URL)
        self.headers = {
            "User-Agent": "civicband-clerk (+https://civic.band)",
            "Referer": self.calendar_url,
        }
        self.logger.log(f"Initializing San Francisco CA Fetcher for {self.subdomain}")

    @staticmethod
    def _postback_fields(soup: BeautifulSoup) -> dict[str, str]:
        """Return ASP.NET state needed for the next postback."""
        return {
            str(element["name"]): str(element.get("value", ""))
            for element in soup.select('input[type="hidden"][name]')
        }

    @staticmethod
    def _page_targets(soup: BeautifulSoup) -> list[tuple[int, str]]:
        """Extract numbered Telerik pager postback targets."""
        targets: list[tuple[int, str]] = []
        pager = soup.select_one("tr.rgPager")
        if pager is None:
            return targets
        for link in pager.select("a[href]"):
            label = link.get_text(strip=True)
            match = re.search(r"__doPostBack\('([^']+)'", str(link.get("href", "")))
            if label.isdigit() and match:
                targets.append((int(label), match.group(1)))
        return sorted(targets)

    def _post(
        self,
        soup: BeautifulSoup,
        target: str,
        cookies: dict[str, str],
        **fields: str,
    ) -> BeautifulSoup:
        data = self._postback_fields(soup)
        data.update(fields)
        data["__EVENTTARGET"] = target
        data["__EVENTARGUMENT"] = ""
        response = self.request(
            "POST",
            self.calendar_url,
            data=data,
            headers=self.headers,
            cookies=cookies,
        )
        if response is None:
            raise RuntimeError(f"San Francisco calendar postback failed: {target}")
        response.raise_for_status()
        cookies.update(dict(response.cookies))
        return BeautifulSoup(response.text, "html.parser")

    def _year_pages(
        self, initial_soup: BeautifulSoup, cookies: dict[str, str], year: int
    ) -> Iterator[BeautifulSoup]:
        soup = self._post(
            initial_soup,
            YEAR_EVENT_TARGET,
            cookies,
            **{YEAR_CLIENT_STATE: json.dumps({"value": str(year)})},
        )
        yield soup

        # Legistar limits the grid to 100 rows. Each page response contains
        # fresh ASP.NET state, so post back sequentially through its pager.
        for page, target in self._page_targets(soup):
            if page == 1:
                continue
            soup = self._post(soup, target, cookies)
            yield soup

    def _fetch_document(
        self, link: Tag | None, kind: str, meeting_name: str, date_string: str
    ) -> bool:
        href = link.get("href") if link else None
        if not isinstance(href, str) or not href:
            return False
        if self.check_if_exists(meeting_name, date_string, kind):
            return False
        output_dir = (
            self.minutes_output_dir if kind == "minutes" else self.agendas_output_dir
        )
        Path(output_dir, meeting_name).mkdir(parents=True, exist_ok=True)
        self.fetch_and_write_pdf(
            urljoin(self.calendar_url, href),
            kind,
            meeting_name,
            date_string,
        )
        return True

    def _process_page(self, soup: BeautifulSoup) -> tuple[int, int]:
        events = 0
        minutes = 0
        for row in soup.select(ROW_SELECTOR):
            cells = row.find_all("td", recursive=False)
            body_link = row.select_one('a[id$="_hypBody"]')
            if len(cells) < 2 or not isinstance(body_link, Tag):
                continue

            date_text = cells[1].get_text(strip=True)
            try:
                month, day, year = (int(part) for part in date_text.split("/"))
                meeting_date = date(year, month, day)
            except (TypeError, ValueError):
                self.logger.log(
                    f"Skipping meeting with invalid date: {date_text}",
                    level="warning",
                )
                continue

            events += 1
            date_string = meeting_date.isoformat()
            meeting_name = self.simplified_meeting_name(body_link.get_text(strip=True))

            minutes_link = row.select_one('a[id$="_hypMinutes"]')
            if self._fetch_document(
                minutes_link if isinstance(minutes_link, Tag) else None,
                "minutes",
                meeting_name,
                date_string,
            ):
                minutes += 1

            agenda_link = row.select_one('a[id$="_hypAgenda"]')
            if (
                self.all_agendas or meeting_date >= self.today.date()
            ) and self._fetch_document(
                agenda_link if isinstance(agenda_link, Tag) else None,
                "agenda",
                meeting_name,
                date_string,
            ):
                self.total_agendas += 1

        return events, minutes

    @override
    def fetch_events(self) -> tuple[int, int]:
        response = self.request("GET", self.calendar_url, headers=self.headers)
        if response is None:
            raise RuntimeError("Failed to fetch the San Francisco meeting calendar")
        response.raise_for_status()
        initial_soup = BeautifulSoup(response.text, "html.parser")
        cookies = dict(response.cookies)

        for year in range(self.start_year, self.today.year + 1):
            for soup in self._year_pages(initial_soup, cookies, year):
                events, minutes = self._process_page(soup)
                self.total_events += events
                self.total_minutes += minutes
                initial_soup = soup
        return self.total_events, self.total_minutes
