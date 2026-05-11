import os
from datetime import datetime
from typing import TypeAlias

from clerk import Fetcher
from parsedatetime import Calendar

calendar = Calendar()


class BerkeleyCAFetcher(Fetcher):
    def child_init(self):
        self.logger.log("Initializing Berkeley CA Fetcher")

    def fetch_events(self):
        total_events = 0
        total_minutes = 0
        terms = [
            "agenda",
            "aging",
            "arts",
            "board",
            "campaign",
            "cannabis",
            "childhood",
            "civic",
            "commission",
            "disability",
            "disaster",
            "downtown",
            "elmwood",
            "energy",
            "finance",
            "health",
            "homeless",
            "housing",
            "joint",
            "landmarks",
            "library",
            "loan",
            "medical",
            "meeting",
            "minutes",
            "oakland",
            "alameda",
            "albany",
            "city",
            "parks",
            "peace",
            "personnel",
            "planning",
            "police",
            "policy",
            "public",
            "redevelopment",
            "redistricting",
            "rent",
            "street",
            "successor",
            "sugar",
            "tax",
            "transportation",
            "university",
            "waste",
            "waterfront",
            "welfare",
            "youth",
        ]

        for term in terms:
            json_data = {
                "SearchText": term,
                "QueryID": 115,
                "Keywords": [
                    {
                        "ID": 123,
                        "Value": "",
                        "KeywordOperator": "=",
                    },
                ],
                "QueryLimit": 0,
                "FromDate": f"{self.start_year}-01-01T08:00:00.000Z",
            }
            try:
                fetched_events, fetched_minutes = self.fetch_from_json(json_data)
                total_events += fetched_events
                total_minutes += fetched_minutes
            except TypeError:
                self.logger.log(
                    f"Error fetching data for {json_data['SearchText']}", level="error"
                )
                continue
        return total_events, total_minutes

    def fetch_from_json(self, json_data) -> tuple[int, int]:
        fetched_events = 0
        fetched_minutes = 0

        cookies = {
            "cookiesession1": "678A3E8EC1F0126650FA101BAC3C9DBE",
            "ASP.NET_SessionId": "jqf1abt2fo1c10svhzkurz22",
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://records.cityofberkeley.info",
            "Referer": "https://records.cityofberkeley.info/PublicAccess/paFiles/cqFiles/index.html",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        response = self.request(
            "POST",
            "https://records.cityofberkeley.info/PublicAccess/api/DocumentType/FullTextSearch",
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        if response and not response.json():
            self.logger.log(f"No data found for {json_data['SearchText']}")
            return 0, 0
        try:
            items = response.json()["Data"]
        except KeyError:
            self.logger.log("Error fetching items from response", level="error")
            return 0, 0
        self.logger.log(f"fetched {len(items)} for {json_data['SearchText']}")
        for item in items:
            fetched_events += 1
            try:
                # raw_date, _, body_name, _, _ = item["Name"].split("; ")
                metadata = item["Name"].split("; ")
                raw_date = metadata[0]
                body_name = metadata[2]
            except:
                self.logger.log(item["Name"], level="warning")
                continue
            time_struct, _ = calendar.parse(raw_date)
            current_item_datetime = datetime(*time_struct[:6])
            date_string = current_item_datetime.strftime("%Y-%m-%d")
            body_name = (
                body_name.replace(" of ", "Of")
                .replace(" on ", "On")
                .replace(" and ", "And")
                .replace(" ", "")
            )
            if not body_name:
                self.logger.log(item["Name"], level="warning")
                continue
            directory = f"{self.storage_dir}/{self.subdomain}/pdfs/{body_name}"
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = date_string + ".pdf"
            filepath = f"{directory}/{filename}"
            if self.check_if_exists(body_name, date_string, "minutes"):
                self.logger.log(f"{filepath} already exists, skipping")
                continue
            pdf_url = f"https://records.cityofberkeley.info/PublicAccess/api/Document/{item['ID'].replace('=', '%3D')}"
            pdf_response = self.request("GET", pdf_url)
            with open(filepath, "wb") as pdf_file:
                pdf_file.write(pdf_response.content)
                fetched_minutes += 1
        self.logger.log(f"done fetching for {json_data['SearchText']}")
        return fetched_events, fetched_minutes
