# FAQs

Before you dive too deep here, you might want to start with our [Contributors' Guide](CONTRIBUTING.md) and overall [Readme](README.md). If you've read those and still need more answers, 
check out the info here! If you still have questions after that, you can join the [Zulip](https://civictown.zulipchat.com/join/jmprqfsjk63a5fqwkq3kafvr/) to ask or open an [Issue](https://github.com/civicband/clerk-fetchers/issues) on this repository. 

# What's a municipality?
Municipalities are civic bodies like cities, towns, boroughs, counties, and public boards (like a School Board or a Port District Oversight Board). For Civic Band's purposes, states and countries do not count as municipalities.

# How can I tell if my municipality uses a supported backend, or if we need a custom scraper?

We have a WIP-draft Chrome extension experiment that should be able to help you tell, but it's not really ready to use yet. For now, navigate to the page that has the actual PDFs of your meeting minutes as best you can and look for the names of the supported scrapers in the URL, around the top of the page, and in the page's meta data when you **View Source**. If that sounds like too much, you can leave a note in the issue that says you're not sure whether it needs a custom scraper or not, and a maintainer will check it out for you.

# Why would I need a custom scraper?

You would need a custom scraper to get information off of a page that doesn't use a backend we support. Right now, anything that doesn't use an already-supported backend says to use a custom scraper. If we end up with two or more cities using the same backend that we don't support yet, though, we can add a new reusable scraper for them. Please let us know if you see this, and we'll keep an eye out as well.

# What if my municipality hosts minutes/agendas in multiple places?

Right now, due to technical limitations, we ask that you just pick one primary scraper to use. We have an [open issue](https://github.com/civicband/clerk/issues/6) to fix this in the [Clerk](https://github.com/civicband/clerk/) repository, and it has a [subtask](https://github.com/civicband/clerk/issues/145#issue-4471550967) to update this FAQ when it's fixed.
