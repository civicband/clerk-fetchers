from clerk_fetchers.fetchers.example_city import ExampleCityFetcher
from clerk_fetchers.fetchers.berkeley_ca import BerkeleyCAFetcher
from clerk_fetchers.fetchers.rutherford_nj import RutherfordNJFetcher


FETCHER_REGISTRY = {
    "example_city": ExampleCityFetcher,
    "berkeley.ca": BerkeleyCAFetcher,
    "rutherford.nj": RutherfordNJFetcher,
}

EXTRA_REGISTRY = {
    "example_city": {"base_url": "https://example-city.gov/meetings"},
}
