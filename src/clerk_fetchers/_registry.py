from clerk_fetchers.fetchers.example_city import ExampleCityFetcher
from clerk_fetchers.fetchers.berkeley_ca import BerkeleyCAFetcher


FETCHER_REGISTRY = {
    "example_city": ExampleCityFetcher,
    "berkeley.ca": BerkeleyCAFetcher,
}

EXTRA_REGISTRY = {
    "example_city": {"base_url": "https://example-city.gov/meetings"},
}
