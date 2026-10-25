# Architecture

## Stack

Python 3.12/3.13, Django 5.2 LTS, server-rendered templates, plain CSS and small progressive-enhancement JavaScript. SQLite locally; PostgreSQL configurable in production. WhiteNoise serves collected static assets. Nginx/Passenger serves uploaded photos. There is no Node build dependency for the delivered site.

## Main records

- Source: reference title, URL and editorial notes.
- Plant: five-language JSON fields, botanical facts, photo and editorial status.
- Region: named area, climate/soil descriptions and optional weather coordinates.
- PlantingWindow: plant + region + action, month list, source and review flag.
- Guide: home/soil/equipment/diary content with translation dictionaries.
- GardenEntry: user-owned planting date, care date, notes and growth status.
- RequestBucket: short-lived hashed-IP anti-abuse counters.
- Standard Django User / sessions; Axes login protection tables; shared weather cache table.

## Request flow

Public requests → middleware / language preference → validated query parameters → ORM → escaped templates. Plant search matches all five names plus scientific name. Recommendation rules match region, month, minimum sun, container suitability and indoor category. No AI-generated result is created on demand.

Authenticated mutations → session + CSRF → owner-scoped queryset / form validation → database transaction. Public users never control owner or staff status.

Weather is optional and server-side. Static knowledge remains usable during outages. Bundled photographs remove per-visit image-API calls. Five-language text is stored once, not translated per request.

## Files

- config/: environment-driven settings, WSGI/ASGI and routes.
- garden/: models, forms, views, services, security, templates tags, admin and tests.
- templates/: public, account and error screens.
- static/garden/: CSS, JavaScript, favicon and photos.
- data/: original seed content and third-party asset credits.
- deploy/: example Nginx/systemd configuration.
- scripts/: development setup and SQLite backup.
- docs/: installation, content, security, deployment and test report.

## Costs

Core content and recommendation functionality makes zero external API calls. Hosting, domain renewal, optional SMTP and any future commercial weather service have their own provider costs. Existing hosting quotas still apply.

## Extending carefully

To add a new language, add its code to LANGUAGES, labels, translations and search tests. To add a plant, use admin with sources/photos and calendar windows. To add a region, create a Region and reviewed windows; no automatic neighbouring-city extrapolation occurs. For reminders later, use an opt-in background worker/cron workflow with consent and retry/deduplication rather than sending mail during page views.
