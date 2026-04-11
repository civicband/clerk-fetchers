# Contributing to clerk-fetchers

There are two ways to contribute fetchers to the clerk ecosystem:

1. **Add a fetcher to this package** (recommended for most contributors)
2. **Publish your own independent fetcher package**

## Adding a fetcher to clerk-fetchers

### 1. Fork and branch

Fork this repository and create a feature branch for your fetcher.

### 2. Create your fetcher directory

Create a new directory under `src/clerk_fetchers/fetchers/` named after the municipality:

```
src/clerk_fetchers/fetchers/your_city_name/
├── __init__.py   # Your Fetcher subclass
└── README.md     # Documentation for this fetcher
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

See `src/clerk_fetchers/fetchers/example_city/` for a complete reference implementation.

### 4. Register the fetcher

Add your fetcher to `src/clerk_fetchers/_registry.py`:

```python
from clerk_fetchers.fetchers.your_city_name import YourCityFetcher

FETCHER_REGISTRY = {
    "example_city": ExampleCityFetcher,
    "your_city_name": YourCityFetcher,  # Add your entry
}

EXTRA_REGISTRY = {
    "example_city": {"base_url": "https://example-city.gov/meetings"},
    "your_city_name": {"base_url": "https://your-city.gov/meetings"},  # Add defaults
}
```

### 5. Write a fetcher README

Document your fetcher in `src/clerk_fetchers/fetchers/your_city_name/README.md`:

- Target site URL
- Extra config keys and their defaults
- Known quirks or limitations

### 6. Write tests

Create tests in `tests/fetchers/your_city_name/`:

```
tests/fetchers/your_city_name/
├── __init__.py
├── test_fetcher.py
└── fixtures/
    └── meetings_page.html   # Saved HTML/JSON responses from the target site
```

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
