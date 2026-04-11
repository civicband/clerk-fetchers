# Example City Fetcher

A reference fetcher implementation for `clerk-fetchers`. Use this as a template when building your own fetcher.

## Target Site

https://example-city.gov/meetings (hypothetical)

## Extra Config Keys

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `base_url` | No | `https://example-city.gov/meetings` | URL of the meetings listing page |

## How It Works

1. Fetches the meetings listing page
2. Parses `<tr class="meeting-row">` elements
3. Extracts meeting title, date, and minutes PDF link
4. Downloads any linked PDF minutes

## Known Quirks

This is a reference implementation against a hypothetical site. It demonstrates:

- Parsing extra config from `self.site["extra"]`
- Using `self.request()` for HTTP calls
- Using BeautifulSoup for HTML parsing
- Using `self.fetch_and_write_pdf()` for PDF downloads
- Using `self.simplified_meeting_name()` for consistent naming
