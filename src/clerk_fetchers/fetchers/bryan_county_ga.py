from bs4._typing import _AttributeValue


from httpx._models import Response


from clerk import Fetcher
from bs4 import BeautifulSoup
from dateutil.parser import parse


class BryanCountyGAFetcher(Fetcher):
    def child_init(self):
        self.base_url = "https://www.bryancountyga.gov"
        self.assert_fetch_dirs()
        self.assert_processed_dirs()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:157.0) Gecko/20100101 Firefox/157.0",
            "X-Who-Am-I": "CivicBand (hello@civic.band)",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "DNT": "1",
            "Sec-GPC": "1",
            "Priority": "u=0, i",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

    def fetch_events(self) -> None:
        self.base_url = "https://www.bryancountyga.gov"

    def fetch_agendas(self):
        self.agendas_url = f"{self.base_url}/government/board-of-commissioners/agendas"
        response: Response | None = self.request(
            method="GET", url=self.agendas_url, headers=self.headers
        )
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select("#widget_321_442_169 li a")
        for link in links:
            year = link.text.strip()
            href: _AttributeValue | None = link.get("href")
            if href and year == "2014":
                year_url = f"{self.base_url}{href}"
                year_response = self.request(
                    method="GET", url=year_url, headers=self.headers
                )
                year_soup = BeautifulSoup(year_response.text, "html.parser")
                agenda_links = year_soup.select("#widget_321_447_171 li a")
                for agenda_link in agenda_links:
                    meeting_name = None
                    if len(agenda_link.text.split("Agenda")) > 0:
                        meeting_name = "Agenda"
                        if len(agenda_link.text.split("Pre-Agenda Meeting")) > 1:
                            meeting_name = "Pre-Agenda Meeting"
                        if len(agenda_link.text.split("Regular Meeting")) > 1:
                            meeting_name = "Regular Meeting"
                        if len(agenda_link.text.split("Special Called Meeting")) > 1:
                            meeting_name = "Special Called Meeting"
                        if len(agenda_link.text.split("Called Meeting")) > 1:
                            meeting_name = "Called Meeting"
                        if len(agenda_link.text.split("Workshop")) > 1:
                            meeting_name = "Workshop"
                            if (
                                meeting_name == "Workshop"
                                and "UDO BOC" in agenda_link.text
                            ):
                                meeting_name = "UDO BOC Workshop"

                    if meeting_name:
                        try:
                            meeting_date = parse(
                                agenda_link.text.split(meeting_name)[0].strip()
                            )
                        except Exception as e:
                            self.logger.log(
                                f"Error parsing meeting date from text: {agenda_link.text}",
                                level="error",
                                error=str(e),
                            )
                            continue
                        meeting_name = self.simplified_meeting_name(meeting_name)
                        agenda_href: _AttributeValue | None = agenda_link.get("href")
                        if agenda_href and meeting_date:
                            self.fetch_and_write_pdf(
                                url=f"{self.base_url}{agenda_href}",
                                kind="agenda",
                                date=meeting_date.strftime("%Y-%m-%d"),
                                meeting=meeting_name,
                                headers=self.headers,
                            )

    def fetch_minutes(self):
        self.minutes_url = f"{self.base_url}/government/board-of-commissioners/minutes"
        response: Response | None = self.request(
            method="GET", url=self.minutes_url, headers=self.headers
        )
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select("#widget_321_447_171 li a")
        for link in links:
            year = link.text.strip()
            href: _AttributeValue | None = link.get("href")
            if href and year == "2014":
                year_url = f"{self.base_url}{href}"
                year_response = self.request(
                    method="GET", url=year_url, headers=self.headers
                )
                year_soup = BeautifulSoup(year_response.text, "html.parser")
                minutes_links = year_soup.select("#widget_321_447_171 li a")
                for minutes_link in minutes_links:
                    meeting_name = None
                    if len(minutes_link.text.split("Regular Meeting")) > 0:
                        meeting_name = "Regular Meeting"
                    if len(minutes_link.text.split("Special Called Meeting")) > 1:
                        meeting_name = "Special Called Meeting"
                    if len(minutes_link.text.split("Pre-Agenda Meeting")) > 1:
                        meeting_name = "Pre-Agenda Meeting"
                    if len(minutes_link.text.split("Called Meeting")) > 1:
                        meeting_name = "Called Meeting"
                    if len(minutes_link.text.split("Workshop")) > 1:
                        meeting_name = "Workshop"
                        if meeting_name == "Workshop" and "UDO" in minutes_link.text:
                            meeting_name = "UDO Workshop"

                    if meeting_name:
                        try:
                            meeting_date = parse(
                                minutes_link.text.split(meeting_name)[0].strip()
                            )
                        except Exception as e:
                            self.logger.log(
                                f"Error parsing meeting date from text: {minutes_link.text}",
                                level="error",
                                error=str(e),
                            )
                            continue
                        meeting_name = self.simplified_meeting_name(meeting_name)
                        minutes_href: _AttributeValue | None = minutes_link.get("href")
                        if minutes_href and meeting_date:
                            self.fetch_and_write_pdf(
                                url=f"{self.base_url}{minutes_href}",
                                kind="minutes",
                                date=meeting_date.strftime("%Y-%m-%d"),
                                meeting=meeting_name,
                                headers=self.headers,
                            )
