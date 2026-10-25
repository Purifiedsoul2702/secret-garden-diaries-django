# Secret Garden Diaries

A complete, server-rendered **Python + Django** gardening website for Indian homes. No Node.js build, paid API, cloud database or external image service is required to run the delivered application.

## Start here

- Windows / VS Code: [docs/INSTALL_WINDOWS.md](docs/INSTALL_WINDOWS.md)
- Hosting, VPS and cPanel: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- Content, translations and admin: [docs/CONTENT_GUIDE.md](docs/CONTENT_GUIDE.md)
- Security and operations: [docs/SECURITY.md](docs/SECURITY.md)
- Architecture / features: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Test results: [docs/TEST_REPORT.md](docs/TEST_REPORT.md)
- Photograph credits: [data/ASSET_CREDITS.json](data/ASSET_CREDITS.json)

## Quick start (Python 3.12 or 3.13)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux instead:
# source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_local.py
python manage.py migrate
python manage.py createcachetable
python manage.py seed_garden
python manage.py createsuperuser
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** and **http://127.0.0.1:8000/admin/**. You choose your own administrator credentials. There are no default accounts or passwords. SQLite is created by migrations; a private populated database is intentionally not shipped.

## Included

- Responsive cream-and-forest-green design, locally bundled real photographs, accessible labels, mobile menu, keyboard focus and no remote fonts.
- Searchable plant library, category / beginner / container filters and pagination.
- English, Hindi, Marathi, Tamil and Bangla plant names, summaries, care and soil text, plus translated primary navigation and selected full guides.
- Regional planting finder by growing area, month, direct sunlight and space. Source-linked starter calendars show their editorial status.
- Soil and climate pages, home gardening, tools/equipment and garden diary articles.
- Registration, login, logout, password recovery and account deletion.
- Private garden entries, planting dates, care due dates, notes, statuses, editing, deletion and safe CSV export.
- Django admin for plant / article / translation / source / region management and validated, sanitised photo uploads.
- Optional server-side Open-Meteo weather with caching and graceful failure; off by default.
- Security headers, CSRF protection, escaped content, login lockouts, account/recovery rate limits, HTTPS production defaults, hardened upload handling and automated tests.
- Sitemap, robots.txt, health endpoint, migrations, deployment samples and backup/cleanup utilities.

## Honest scope

This is a working application, not a fully reviewed national agronomy database. The seed includes **12 plants, six example areas and eight guides**. All 72 planting windows are broad **draft** guidance. Regional climate/soil descriptions and some long articles/account labels remain English; missing article translations are disclosed. Plant translations and regional recommendations need language/agronomy review before public launch. No expert approval is implied by a source link.

The site does not identify plants from photos, run a chatbot, scrape the web on demand, sell equipment, send scheduled reminders or provide exact soil chemistry by address. Care dates are visible in My Garden. These exclusions avoid recurring costs and unsupported claims.

Your hosting must support Python WSGI/Passenger or a VPS. Ordinary PHP-only hosting cannot execute Django. See the hosting guide before uploading anything publicly.

## Test

```bash
python manage.py test garden
python manage.py check
```

Use `python manage.py check --deploy` with a fully configured production environment. A local development environment deliberately fails production checks.

## Licensing

Original application code: MIT (LICENSE). Included third-party photographs retain their own licences and attribution requirements; see the credits JSON. CC BY-SA photographs and resized derivatives retain that image licence. They do not relicense the application code. Reference articles are linked, not copied in full.
