# Clerk Fetchers Chrome Extension Readme

** Note: ** This is not the full-repository readme, which can be found at [ReadMe.md](README.md). Check out the [Contributor Guide](CONTRIBUTING.md) to get started! 

## Description

This Chrome extension lets the community easily check whether a set of civic meeting data you'd like to add to CivicBand is likely hosted through an already-supported backend. If you install this Chrome extension, you can click it while on a Civic Meeting data page to see a popup letting you know whether the page is:
    - likely meeting data from a supported backend, and if so, which one
    - almost-but-not-quite the page we scrape
    - a page that might require a custom scraper.

We request this information in issues, and the Chrome Extension should make it easier to get! 

## Getting Started

### Dependencies

* Google Chrome 148+

Note: This might also work on other browsers that support the `browser` API that replaced the `chrome` API in Chrome 148, but it hasn't been tested there yet.

### Setup

1. Download this `utilities/Chrome Extension` folder or checkout this repository.
1. In the Chrome browser, go to chrome://extensions to view the Extension page.
1. In the top right corner of the page, toggle on ** Developer mode **. 
1. In the top-left, click Load Unpacked.
1. Select the `utilities/Chrome Extension` folder on your local machine. 
1. Click ** Select ** to load it in.
You can now use this extension like any other!

### Using It

First navigate to the page you would download a PDF of your civic meeting data from. If your civic meeting minutes aren't available as a PDF, log your issue with the "Custom Scraper" backend chosen.

Click the extension to see which backend is in use, then you'll have that information to use here!

## Help

Open a [GitHub issue](../../issues) to report bugs or request help you're trying to add. To reach the maintainers privately, email Philip at [hello@civic.band](mailto:hello@civic.band).

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.