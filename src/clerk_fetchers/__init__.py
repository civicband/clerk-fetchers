from clerk import hookimpl

from clerk_fetchers._registry import EXTRA_REGISTRY, FETCHER_REGISTRY


class ClerkFetchersPlugin:
    @hookimpl
    def fetcher_class(self, label):
        return FETCHER_REGISTRY.get(label)

    @hookimpl
    def fetcher_extra(self, label):
        return EXTRA_REGISTRY.get(label)


__version__ = "0.0.4"
