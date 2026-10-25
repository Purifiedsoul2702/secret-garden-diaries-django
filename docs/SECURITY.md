# Security design and operational limits

## Implemented controls

- Django 5.2 LTS patch pinned in requirements; ORM queries, CSRF middleware, autoescaped templates, validated forms and explicit host allowlisting.
- No public rich HTML, arbitrary URL fetch, uploaded HTML/SVG, paid AI integration or client-side API secrets.
- Production refuses missing/short/example secrets and wildcard/empty hosts. DEBUG defaults false. HTTPS redirect, secure cookies, HttpOnly sessions, SameSite=Lax, HSTS, no-sniff and DENY frame policy.
- Public CSP permits only same-origin scripts/styles/images (data images allowed); no inline script and no third-party runtime assets. Admin allows inline CSS for Django widgets but not inline scripts. Verify CSP again after third-party plugin changes.
- Django password hashing and validators, 12-character minimum, one-hour recovery links, POST logout, and no default credentials.
- django-axes locks login after five failures for username or IP, with a 30-minute cooloff. Admin login is covered. Public registration and password recovery are limited per hashed connection IP by persistent database counters.
- Source IP comes from REMOTE_ADDR unless the immediate peer is explicitly trusted. Only then is validated X-Real-IP accepted. Never trust arbitrary X-Forwarded-For. Shared IPs can share limits; tune at the trusted proxy as needed.
- Garden reads/updates/deletes/exports are scoped to the authenticated owner. A posted owner ID is ignored. Destructive actions require POST and CSRF; account deletion reauthenticates the same user.
- Notes are escaped and CSV cells with formula prefixes are neutralised.
- Staff-only photo uploads are size/type/dimension checked, re-encoded to JPEG with random filenames, and original metadata removed.
- Private/account/admin responses have no-store caching. Public user journals are not registered in Django admin.
- Weather fetches a fixed HTTPS host with staff-configured coordinates, a 4-second timeout, response size bound, shared cache and error fallback. Users cannot make the server fetch arbitrary URLs.

## What this does NOT promise

No penetration test or formal security audit has been performed. No software is invulnerable. Admin MFA is not bundled; protect admin through a VPN/IP allowlist or an MFA-capable access gateway. Signup does not verify email ownership. There is no DDoS defence, bot CAPTCHA, antivirus service or external monitoring. SQLite counter behaviour under heavy concurrent writes is not a substitute for proxy rate limiting/PostgreSQL. Hosting configuration, patching and correct proxy trust remain essential.

## Operator tasks

- Keep secrets out of Git and backups shared publicly. Rotate credentials after suspected exposure.
- Use strong unique administrator passwords, least-privilege staff permissions and no shared staff accounts.
- Run `python manage.py check --deploy` under production settings. Run tests before updates.
- Audit installed dependencies periodically, update supported security releases and rebuild your environment. The pinned file is a reproducible starting point, not a forever-safe version list.
- Log errors without private journal contents or credentials. Protect access logs and backup retention. Run `cleanup_security` daily and `clearsessions` periodically.
- Back up the database and uploads, test restores, and monitor storage quotas.
- If locked out, use the operator-only `python manage.py axes_reset` command via your trusted terminal.
- Expose only HTTPS and required SSH management. Serve uploads as non-executable assets. Never use Django runserver for public production.

## Reporting

Before public launch, add your operator contact details to the privacy page and your own vulnerability reporting address here. Do not publish a contact address that you do not control.
