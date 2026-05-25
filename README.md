# Clerk-Fetchers

This repository lets the community contribute additional fetchers for municipal government meeting minutes and agendas to extend [Clerk]. Check out the [Contributor Guide](CONTRIBUTING.md) and included example to get started! 

## Description

A community-contributed repository that extends [Clerk] with fetchers for non-standard municipal government meeting minutes and agendas. Each fetcher targets a specific municipality, scraping meeting listings and downloading associated PDFs. 

Anyone can add new fetchers following the included example and [Contributor Guide](CONTRIBUTING.md).

These fetchers, if accepted, will feed PDFs into CivicBand's pipeline. Data will be available for search approximately 24 business hours after the first successful fetcher run. 

## Getting Started

### Dependencies

* Python 3.12+
* UV package manager
* [clerk] >= 0.0.1
* Dev dependencies: `pytest>=7.4.0`, `respx>=0.23.0`, `hatchling` build system

### Developer Setup

See [**Adding a fetcher to clerk-fetchers**](CONTRIBUTING.md#adding-a-fetcher-to-clerk-fetchers) in the Contributor Guide for full setup instructions. At a high level:

1. Fork this repo and create a feature branch
2. Add your fetcher under `src/clerk_fetchers/fetchers/<municipality_name>/`
3. Register it in `src/clerk_fetchers/_registry.py`
4. Write tests in `tests/fetchers/<municipality_name>/`
5. Open a PR — CI will run the full test suite

### Testing

Run `pytest` locally to check your fetcher before submitting. CI also runs the full test suite automatically once you open a PR.

### After Submission

One of the maintainers will review your PR at our earliest convenience. We might have follow-up questions, which we'll post either as a comment on the PR (for overall/general feedback) or using the GitHub reviews workflow (for line-specific feedback). If we don't get a response to questions about your PR within a month, we'll close the PR to avoid stale PR buildup. You should feel free to reopen it when you come back, though! 

## Help

Open a [GitHub issue](../../issues) to report bugs or request help with a fetcher you're trying to add. To reach the maintainers privately, email Philip at [hello@civic.band](mailto:hello@civic.band).

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

[Clerk]: https://github.com/civicband/clerk
