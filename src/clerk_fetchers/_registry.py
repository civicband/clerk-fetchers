from clerk_fetchers.fetchers.example_city import ExampleCityFetcher

FETCHER_REGISTRY = {
    "example_city": ExampleCityFetcher,
}

EXTRA_REGISTRY = {
    "example_city": {"base_url": "https://example-city.gov/meetings"},
}
