# Deploy on your existing domain and hosting

## First: hosting compatibility

Your domain alone does not run Python. Ask your hosting provider: “Does my plan support Python 3.12/3.13 web applications with Passenger/WSGI, virtual environments, persistent storage, HTTPS and cron?” If it only supports PHP/WordPress, deploy Django on a Python-capable host and point the domain there. No universal cPanel path can be supplied without knowing the host.

## Production preparation

1. Back up the existing website and database. Keep it until the new site is verified. Map old blog URLs to new relevant pages with 301 redirects; this project cannot guess your old URLs.
2. Extract source into a private application directory, **not a publicly downloadable document root**. Never expose `.env`, source, backups or `db.sqlite3` through a generic file server.
3. Create a virtualenv and install `requirements.txt`.
4. Copy `.env.example` to `.env`. Generate a secret with `python -c "import secrets; print(secrets.token_urlsafe(64))"` and insert it privately. Use DEBUG=false, exact hostnames and HTTPS trusted origins. Never reuse the example placeholder or your development secret.
5. Configure PostgreSQL for a busy/multiworker public site. SQLite is supported for a small single-instance deployment but serialises writes. PostgreSQL credentials come from your host; there are none in this archive. Remote databases should use TLS and the provider's certificate-verification guidance.
6. Configure SMTP from your hosting provider and verify password recovery before allowing public accounts. Use a domain you own in DEFAULT_FROM_EMAIL. The application has no email verification step; email is for recovery only.
7. Run:

```bash
python manage.py migrate
python manage.py createcachetable
python manage.py seed_garden
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py check --deploy
```

`seed_garden` is idempotent and never overwrites edited records. Run schema migrations on every application update. Back up first.

## cPanel / Passenger

- In “Setup Python App”, select a supported interpreter and your private application root.
- Set startup file `passenger_wsgi.py`, application entry point `application`, and your domain/application URL.
- Use the virtualenv activation command provided by cPanel, then install dependencies and run the commands above.
- Supply environment variables through the panel or a private `.env`. Configure the host's HTTPS forwarding correctly. Do not disable HTTPS security to fix a proxy loop.
- WhiteNoise serves collected static files. Have the hosting provider map `/media/` to the media directory as non-executable static files; Django does not serve production uploads itself.
- Restart the Python app through the panel. Exact UI and paths vary by provider.
- If mounted at a subpath, this project needs URL/static prefix configuration; deployment at the domain root is the documented default.

## Linux VPS: Gunicorn + Nginx

1. Create a dedicated unprivileged `secretgarden` OS user. Put the project in `/srv/secret-garden-diaries`. Keep source read-only to the worker where practical; grant write access only to media and SQLite location when used.
2. Create `.venv`, install dependencies and configure `.env` as above. Secure `.env` with chmod 600 or restricted owner/group access. Obtain a TLS certificate using your host's supported method.
3. Adapt `deploy/nginx.conf` and `deploy/secretgarden.service`. The examples bind Gunicorn to localhost port 8001. Do not open port 8001 to the public internet.
4. For this exact Nginx-to-localhost setup, set `TRUST_PROXY_HTTPS=true` and `TRUSTED_PROXY_IPS=127.0.0.1`. Nginx replaces X-Forwarded-Proto and X-Real-IP. Only trust proxy addresses you control. A load balancer/CDN needs its own correctly configured trusted-hop chain.
5. Run `nginx -t`, enable/restart the systemd service, and reload Nginx using your server administration process.
6. Enable HTTPS redirects, inspect cookies/headers, and confirm the health endpoint. Start HSTS only once HTTPS is working; subdomain/preload settings are intentionally off because they affect other services.
7. Restrict admin access at your firewall/VPN/access gateway. Configure a host-level request rate limit and monitoring according to real traffic. The included application protection is not a DDoS defence.

## Daily maintenance

Schedule these from your hosting cron using absolute interpreter and manage.py paths:

```bash
python manage.py cleanup_security
python manage.py clearsessions
```

The shared database cache is created by `createcachetable` and is required if optional weather is enabled. Weather is disabled by default and uses no paid key. Do not enable the free Open-Meteo service on an ad-supported/commercial site without an appropriate licence.

## Backup / restore

For SQLite, use `python scripts/backup_sqlite.py /private/backups/garden-YYYY-MM-DD.sqlite3` (a new filename each time). Back up `media/` separately. For PostgreSQL use `pg_dump` and the provider's restore workflow. Keep encrypted off-server backups and a documented retention period. Test restoration into a private staging environment; a backup is not verified until restored.

## Release checklist

- Replace privacy operator placeholders and review seed content/translations.
- Confirm homepage, photos, all languages, planner, admin, login, reset email and private-entry isolation.
- Run tests and production checks; configure backups and cleanup cron.
- Verify domain, HTTPS, static/media paths and old-URL redirects.
- Keep dependencies patched. Never claim the website is “100% secure”; deployment and future maintenance matter.

### Intentional HSTS choices
The default production configuration may report W005 and W021 because HSTS subdomain coverage and preload are off. Enable HSTS_INCLUDE_SUBDOMAINS only after all subdomains use HTTPS; enable HSTS_PRELOAD only after understanding the preload commitment. Other deployment warnings must be investigated. A test with both flags enabled verifies the fully HTTPS configuration, but does not choose those domain-wide policies for you.
