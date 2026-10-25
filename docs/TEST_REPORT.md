# Validation report

Validated on 24 October 2026 using Python 3.12.14 and Django 5.2.18.

## Automated application tests

**42 tests passed.** Coverage includes:

- Public routes and every seeded plant/guide detail page.
- Five-language plant rendering, multilingual search and safe language redirects.
- Category filters, unpublished records and seed idempotency.
- Region/month/sunlight/space matching and invalid or unsupported planner input.
- CSRF rejection for public and authenticated mutations.
- Private entry ownership isolation, ignored forged owners, escaped notes and CSV formula protection.
- Registration validation/throttling, login lockout, password recovery throttling and a complete password-reset flow.
- Staff-only administration, POST-only deletion/logout and reauthenticated account deletion.
- Upload rejection and image re-encoding to safe filenames.
- Weather disabled mode, network failure fallback and cache reuse.
- Trusted-proxy validation, security headers and bundled asset availability.

Django model/migration checks pass. Production deployment checks pass with DEBUG=false, explicit hosts, secure HTTPS settings and both HSTS subdomain/preload options enabled for the test. The supplied defaults leave those two domain-wide options off intentionally; see DEPLOYMENT.md before enabling them.

## Visual checks

Inspected rendered homepage at desktop width, a 390-pixel mobile layout, expanded mobile navigation and a plant detail page in a browser. Photographs were inspected in a contact sheet. The preview environment could not execute the project's Python interpreter, so browser checks used Django-rendered static snapshots; backend workflows were tested through Django's test client, not a live browser server.

## Deployment limits

The user's live hosting, domain, TLS certificate, SMTP service and PostgreSQL server were not connected or tested. There has been no penetration test or formal security audit. Seed content and translations are editorial drafts and require review. Live weather is optional and off by default; its success/failure behaviour was tested with mocked responses, not a guaranteed live service SLA.

## Clean-install check
A fresh copy excluding local settings/database was bootstrapped successfully: generated a new development secret, applied migrations, created the cache table, seeded all records, collected static files and rendered the main public/account pages. No pre-existing database or hard-coded credentials were needed.
