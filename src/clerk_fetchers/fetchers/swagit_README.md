# Swagit Fetcher

Fetches meeting agendas from municipalities using the Swagit meeting archive platform
(acquired by Granicus ~2020).

## Target URL pattern

```
https://{swagit_subdomain}.new.swagit.com/{archive_path}?view_id={view_id}
```

## Configuration keys

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `swagit_subdomain` | Yes | — | Subdomain segment (e.g. `uplandca`) |
| `view_id` | Yes | — | Numeric archive view ID (e.g. `299`) |
| `archive_path` | No | `city-council-archived-meetings` | Archive listing path |

## Known quirks

- PDF attachments are hosted on `swagit-attachments.granicus.com` regardless of the
  municipality's own domain.
- Archive pagination caps at 200 pages to avoid runaway requests.
- Dates are normalized to ISO-8601 using `parsedatetime`.

## Adding a new Swagit municipality

No new code required. Add entries to both `FETCHER_REGISTRY` and `EXTRA_REGISTRY`
in `_registry.py`:

```python
"yourcity.xx": SwagitFetcher,
```

```python
"yourcity.xx": {"swagit_subdomain": "yourcityxx", "view_id": "NNN"},
```

## Current municipalities

| Registry key | Subdomain | View ID |
|---|---|---|
| `upland.ca` | `uplandca` | `299` |
