# FAQs

Before you dive too deep here, you might want to start with our [Contributors' Guide](CONTRIBUTING.md) and overall [Readme](README.md). If you've read those and still need more answers, 
check out the info here! If you still have questions after that, please join the [Zulip]() to ask or open an [Issue](https://github.com/civicband/clerk-fetchers/issues). 

# How can I tell if my city uses a supported backend, or if we need a custom scraper?
Information coming soon!

# Why would I need a custom scraper?
You would need a custom scraper to get information off of a page that doesn't use a backend we support. Right now, anything that doesn't use an already-supported backend says to use a custom scraper. If we end up with two or more cities using the same backend that we don't support yet, though, we can add a new reusable scraper for them. Please let us know if you see this, and we'll keep an eye out as well.

# What if my municipality hosts minutes/agendas in multiple places?
Right now, due to technical limitations, we ask that you just pick one primary scraper to use. We have an [open issue](https://github.com/civicband/clerk/issues/6) to fix this in the [Clerk](https://github.com/civicband/clerk/) repository, and it has a [subtask](https://github.com/civicband/clerk/issues/145#issue-4471550967) to update this FAQ when it's fixed.
