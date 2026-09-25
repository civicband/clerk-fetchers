# Contributing to clerk-fetchers

There are two ways to contribute fetchers to the clerk ecosystem:

1. **Add a fetcher to this package** (recommended for most contributors)
2. **Publish your own independent fetcher package**

## Existing backends

The `clerk` ecosystem is already capable of handling a variety of known
backends, although the code responsible for this is not visible here. The
currently supported backends are:

- AgendaCenter
- BoardDocs
- CivicClerk
- EBoard
- Escribe
- Granicus
- IQM2
- Laserfiche
- Legistar
- Municode
- OnBase
- PrimeGov

When triaging a municipal site as a source of documents, if you discover that
the site uses one of these services, the good news is that a new `Fetcher` is not
required! Note the URL and which service the site uses on the issue.

## Adding a fetcher to clerk-fetchers

### 1. Fork and branch

Fork this repository and create a feature branch for your fetcher.

### 2. Create your fetcher module

Create a new module under `src/clerk_fetchers/fetchers/` named after the
municipality's subdomain, with `.` replaced by `_` (e.g. the `berkeley.ca`
subdomain lives in `berkeley_ca.py`):

```
src/clerk_fetchers/fetchers/your_city_st.py   # Your Fetcher subclass
```

### 3. Implement the fetcher

Your fetcher must extend `clerk.Fetcher` and implement at minimum `fetch_events()`:

```python
import json
from clerk import Fetcher

class YourCityFetcher(Fetcher):
    def child_init(self):
        extra = self.site.get("extra", "{}")
        if isinstance(extra, str):
            extra = json.loads(extra)
        self.base_url = extra.get("base_url")

    def fetch_events(self):
        # Fetch and parse meeting data from the target site
        # Use self.request() for HTTP calls
        # Use self.fetch_and_write_pdf() for downloading PDFs
        # Track counts with self.total_events and self.total_minutes
        return self.total_events, self.total_minutes
```

See `src/clerk_fetchers/fetchers/example_city.py` for a complete reference implementation.

### 4. Register the fetcher

Add your fetcher to `src/clerk_fetchers/_registry.py`. The registry key is the
site's **subdomain** (e.g. `your_city.st`), matching the existing entries — not
the module filename. Keep the entries after `example_city` alphabetical by
subdomain.

```python
from clerk_fetchers.fetchers.your_city_st import YourCityFetcher

FETCHER_REGISTRY = {
    "example_city": ExampleCityFetcher,
    # Lines should be alphabetical by subdomain from this point
    "your_city.st": YourCityFetcher,  # Add your entry, keyed by subdomain
}
```

`EXTRA_REGISTRY` is optional. Add an entry only if your fetcher needs default
config (such as a `base_url`).

```python
EXTRA_REGISTRY = {
    "example_city": {"base_url": "https://example-city.gov/meetings"},
}
```

### 5. Document your fetcher (optional)

Fetchers don't use a separate README file. If you want to document yours, a
class docstring works well (see `example_city.py`):

- Target site URL
- Extra config keys and their defaults
- Known quirks or limitations

### 6. Write tests

Create tests in `tests/fetchers/your_city_st/`:

```
tests/fetchers/your_city_st/
├── __init__.py
├── test_fetcher.py
└── fixtures/
    └── meetings_page.html   # Saved HTML/JSON responses from the target site
```

HTML fixtures are local HTML files used as mocked responses in tests. For a
municipal site, save the HTML response received by your fetcher, which may
differ from the page after a browser has run JavaScript. Store it under your
test directory's `fixtures/` folder and commit it with the tests so they can run
without contacting the live site.

Keep the markup your parser depends on, including relevant dates and links.
Include representative edge cases, such as a meeting with no minutes link.
The [example HTML fixture](tests/fetchers/example_city/fixtures/meetings_page.html)
contains relative and absolute links as well as a meeting without minutes.
The [example tests](tests/fetchers/example_city/test_fetcher.py) load that file
with `Path.read_text()`, return it in a mocked `httpx.Response` using `respx`, and
mock `fetch_and_write_pdf()` to prevent PDF downloads.

Tests must:
- Use mocked HTTP responses (saved fixtures, not live requests)
- Verify that `fetch_events()` produces the expected results
- Use `respx` (or similar) for HTTP mocking

### 7. Open a PR

CI runs the full test suite. A CivicBand maintainer will review your PR.

## Publishing an independent fetcher package

You can also publish your own standalone package. The pattern is the same:

1. Create a Python package with a `clerk.plugins` entry point
2. Implement `fetcher_class` and optionally `fetcher_extra` hooks
3. Your plugin is discovered automatically when installed alongside clerk

### Minimal pyproject.toml

```toml
[project]
name = "clerk-fetcher-yourcity"
dependencies = ["clerk>=0.0.1"]

[project.entry-points."clerk.plugins"]
clerk-fetcher-yourcity = "your_package:YourPlugin"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Minimal plugin class

```python
from clerk import hookimpl
from your_package.fetcher import YourCityFetcher

class YourPlugin:
    @hookimpl
    def fetcher_class(self, label):
        if label == "your_city":
            return YourCityFetcher

    @hookimpl
    def fetcher_extra(self, label):
        if label == "your_city":
            return {"base_url": "https://your-city.gov/meetings"}
```

This clerk-fetchers repository serves as the reference implementation for this pattern.

# Still Have Questions?
Check out our [FAQs](FAQ.md) for more information about when or why you'd need a custom scraper, how to get started, and more!
