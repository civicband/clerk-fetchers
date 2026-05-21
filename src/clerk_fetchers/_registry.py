from clerk_fetchers.fetchers.alamedausd_ca import AlamedaUSDFetcher
from clerk_fetchers.fetchers.example_city import ExampleCityFetcher
from clerk_fetchers.fetchers.berkeley_ca import BerkeleyCAFetcher
from clerk_fetchers.fetchers.houston_tx import HoustonTXFetcher
from clerk_fetchers.fetchers.senado_pr import SenadoPRFetcher
from clerk_fetchers.fetchers.sanfrancisco_ca import SanFranciscoCAFetcher
from clerk_fetchers.fetchers.swagit import SwagitFetcher


FETCHER_REGISTRY = {
    "example_city": ExampleCityFetcher,
    # Lines should be alphabetical by subdomain from this point
    "alamedausd.ca": AlamedaUSDFetcher,
    "berkeley.ca": BerkeleyCAFetcher,
    "houston.tx": HoustonTXFetcher,
    "sanfrancisco.ca": SanFranciscoCAFetcher,
    "senado.pr": SenadoPRFetcher,
    "upland.ca": SwagitFetcher,
}

EXTRA_REGISTRY = {
    "example_city": {"base_url": "https://example-city.gov/meetings"},
    "upland.ca": {"swagit_subdomain": "uplandca", "view_id": "299"},
}
