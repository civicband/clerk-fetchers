# San Francisco, California

This fetcher reads the official [Board of Supervisors Legistar calendar](https://sfgov.legistar.com/Calendar.aspx). It selects every year from the configured `start_year` through the current year and follows Legistar's 100-item pagination. Published minutes are downloaded; future agendas are downloaded by default. Pass Clerk's `all_agendas` option to backfill historical agendas too.

## Configuration

- `calendar_url` (optional): defaults to `https://sfgov.legistar.com/Calendar.aspx`.

The calendar uses ASP.NET postbacks, so the initial response's cookies and hidden form fields are retained while selecting years and pages.
