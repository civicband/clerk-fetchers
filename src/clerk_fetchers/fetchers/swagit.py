"""Generic Swagit fetcher for civicband-clerk.

Swagit is a video streaming and meeting archive platform used by many
municipalities. It was acquired by Granicus around 2020 but is operationally
distinct from Granicus's primary CMS. Agenda PDFs are hosted on the shared
swagit-attachments.granicus.com host with a consistent path structure across
all Swagit cities, so one parameterized fetcher can serve any of them.

Each Swagit city has:
  * a subdomain at {subdomain}.new.swagit.com
  * a numeric view_id identifying the archive collection (e.g. City Council)

Cities register in EXTRA_REGISTRY with their swagit_subdomain and view_id.
"""

import json
import re
from datetime import datetime

from bs4 import BeautifulSoup
from clerk import Fetcher
from parsedatetime import Calendar


SWAGIT_PDF_URL_PATTERN = re.compile(
    r"https://swagit-attachments\.granicus\.com"
    r"/uploads/video/agenda_file/\d+/[^\"'\s<>]+\.pdf"
)

MEETING_VIDEO_ID_PATTERN = re.compile(r"/videos/(\d+)$")

MAX_ARCHIVE_PAGES = 200


class SwagitFetcher(Fetcher):
    """Generic fetcher for municipalities using Swagit for meeting archives.

    Required extra config:
        swagit_subdomain: subdomain segment, e.g. "uplandca"
        view_id: numeric archive view ID, e.g. "299"

    Optional extra config:
        archive_path: trailing path segment for the archive list
                      (default: "city-council-archived-meetings")
    """

    def child_init(self):
        extra = self.site.get("extra", "{}")
        if isinstance(extra, str):
            extra = json.loads(extra)

        self.swagit_subdomain = extra["swagit_subdomain"]
        self.view_id = str(extra["view_id"])
        self.archive_path = extra.get(
            "archive_path", "city-council-archived-meetings"
        )
        self.base_url = f"https://{self.swagit_subdomain}.new.swagit.com"

    def fetch_events(self):
        page = 1
        while page <= MAX_ARCHIVE_PAGES:
            archive_url = (
                f"{self.base_url}/views/{self.view_id}/"
                f"{self.archive_path}?page={page}"
            )
            resp = self.request("GET", archive_url)
            if not resp:
                break

            meetings = self._parse_archive_page(resp.text)
            if not meetings:
                break

            for video_id, date_text, title in meetings:
                self._process_meeting(video_id, date_text, title)
            page += 1
        else:
            self.logger.log(
                f"Hit MAX_ARCHIVE_PAGES ({MAX_ARCHIVE_PAGES}) for {self.subdomain}",
                level="warning",
            )

        return self.total_events, self.total_minutes

    def _parse_archive_page(self, html: str) -> list[tuple[str, str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        meetings: list[tuple[str, str, str]] = []

        for row in soup.select("table tr"):
            link = row.find("a", href=MEETING_VIDEO_ID_PATTERN)
            if not link:
                continue

            video_id = MEETING_VIDEO_ID_PATTERN.search(link["href"]).group(1)

            date_text = ""
            for td in row.find_all("td"):
                cell_text = td.get_text(strip=True)
                if cell_text and any(c.isdigit() for c in cell_text):
                    date_text = cell_text
                    break

            year_match = re.search(r"\b(\d{4})\b", date_text)
            if year_match and int(year_match.group(1)) < self.start_year:
                # Swagit archives are newest-first; older rows follow, so stop here.
                break

            title = link.get_text(strip=True) or "City Council Meeting"
            meetings.append((video_id, date_text, title))

        return meetings

    def _process_meeting(self, video_id: str, date_text: str, title: str) -> None:
        self.total_events += 1
        meeting_url = f"{self.base_url}/videos/{video_id}"
        resp = self.request("GET", meeting_url)
        if not resp:
            return
        pdf_url = self._extract_agenda_pdf_url(resp.text)
        if not pdf_url:
            return
        self.fetch_and_write_pdf(
            pdf_url,
            "minutes",
            self.simplified_meeting_name(title),
            self._normalize_date(date_text),
        )
        self.total_minutes += 1

    def _normalize_date(self, date_text: str) -> str:
        time_struct, parse_type = Calendar().parse(date_text)
        if parse_type == 0:
            return date_text
        return datetime(*time_struct[:6]).strftime("%Y-%m-%d")

    def _extract_agenda_pdf_url(self, html: str) -> str | None:
        match = SWAGIT_PDF_URL_PATTERN.search(html)
        return match.group(0) if match else None
