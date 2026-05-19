from pathlib import Path

from bs4 import BeautifulSoup
from clerk import Fetcher
from parsedatetime import Calendar

calendar = Calendar()

BASE_URL = "https://www.rutherfordboronj.com"


class RutherfordNJFetcher(Fetcher):
    def child_init(self):
        self.logger.log("Initializing Rutherford NJ Fetcher")
        self.ocr_lang = "eng"

    def fetch_events(self):
        #For now, we are only getting the mayor and council meetings.  In the future,
        # we could add the shade tree commission, rent board, planning board, etc.
        top_level_resp = self.request(
            "GET", f"{BASE_URL}/meetings/meeting-documents/mayor-council-meeting"
        )
        top_level_soup = BeautifulSoup(top_level_resp.text, "html.parser")

        seen = set()
        year_pages = []

        for link in top_level_soup.find_all("a", href=True):
            href = link.get("href", "")
            if "/mayor-council-meeting/" in href and href.count("/") > 3:
                if href in seen:
                    continue
                seen.add(href)
                year = href.split("/")[-1][:4]
                if year.isdigit() and int(year) >= self.start_year:
                    year_pages.append({"year": year, "url": f"{BASE_URL}{href}"})

        for year_page in year_pages:
            self.logger.log(f"Processing year {year_page['year']}")
            year_resp = self.request("GET", year_page["url"])
            year_soup = BeautifulSoup(year_resp.text, "html.parser")

            for link in year_soup.find_all("a", href=True):
                href = link.get("href", "")
                if ("minutes" in href or "agendas" in href) and href.count("/") > 4:
                    if href in seen:
                        continue
                    seen.add(href)
                    kind = "minutes" if "minutes" in href else "agenda"
                    self._fetch_subfolder(f"{BASE_URL}{href}", kind, seen)

    def _fetch_subfolder(self, url, kind, seen):
        resp = self.request("GET", url)
        soup = BeautifulSoup(resp.text, "html.parser")

        for doc_link in soup.find_all("a", href=True):
            doc_href = doc_link.get("href", "")
            if doc_href.endswith("/file") and doc_href != "/meetings/file":
                if doc_href in seen:
                    continue
                seen.add(doc_href)

                slug = doc_href.split("/")[-2]
                date_str = self._parse_date_from_slug(slug)
                if not date_str:
                    self.logger.log(f"Could not parse date from: {slug}", level="warning")
                    continue

                if self.check_if_exists("MayorAndCouncil", date_str, kind):
                    self.logger.log(f"Already exists: {kind} {date_str}, skipping")
                    continue

                output_dir = self.minutes_output_dir if kind == "minutes" else self.agendas_output_dir
                Path(output_dir, "MayorAndCouncil").mkdir(parents=True, exist_ok=True)

                pdf_url = f"{BASE_URL}{doc_href}"
                self.fetch_and_write_pdf(
                    pdf_url, kind, "MayorAndCouncil", date_str
                )

    def _parse_date_from_slug(self, slug):
        from datetime import datetime

        # Strip the leading numeric ID (e.g. "1291-" -> "04-27-2026-mayor...")
        slug = slug.split("-", 1)[1]

        # Truncate after the 4-digit year
        parts = slug.split("-")
        for i, part in enumerate(parts):
            if len(part) == 4 and part.isdigit():
                date_parts = parts[:i + 1]
                break
        else:
            return None

        # parsedatetime needs "/" for numeric dates, spaces for month names
        if all(p.isdigit() for p in date_parts):
            cleaned = "/".join(date_parts)
        else:
            cleaned = " ".join(date_parts)

        time_struct, status = calendar.parse(cleaned)
        if status:
            dt = datetime(*time_struct[:6])
            if dt.year >= 2000:
                return dt.strftime("%Y-%m-%d")
