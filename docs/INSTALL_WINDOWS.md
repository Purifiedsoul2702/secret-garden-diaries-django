# Windows + VS Code installation

1. Install Python 3.12 or 3.13 from python.org. Select **Add Python to PATH**. Restart VS Code after installation.
2. Extract the ZIP. Open the inner `secret-garden-diaries` folder in VS Code. The terminal must be in the folder containing `manage.py` and `requirements.txt`, not its parent.
3. Open Terminal → New Terminal. Run:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/setup_local.py
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py createcachetable
.venv\Scripts\python.exe manage.py seed_garden
.venv\Scripts\python.exe manage.py createsuperuser
.venv\Scripts\python.exe manage.py runserver
```

Use `py -3.13` if that is your installed supported version. Using the full `.venv` interpreter path avoids PowerShell activation-policy issues. No system security-policy change is needed.

4. Open http://127.0.0.1:8000/ . Open /admin/ for the content studio. When typing the administrator password in the terminal, no characters are displayed; this is normal.
5. Stop the server with Ctrl+C. Next time, only run `.venv\Scripts\python.exe manage.py runserver` from the same folder.

## Common problems

- **No module named django:** use the `.venv` interpreter and install requirements.
- **manage.py not found:** open the extracted project folder, not Downloads or C:\Projects alone.
- **SECRET_KEY error:** run `scripts/setup_local.py`. If `.env` already exists, inspect it instead of deleting your production settings. Never paste secrets into public chats.
- **no such table:** run migrations and `createcachetable`.
- **Images missing:** preserve the supplied static directory; run the seed command after extracting all files.
- **Port in use:** `python manage.py runserver 8002`, then visit http://127.0.0.1:8002/ .
- **Login locked:** wait 30 minutes or, as the operator, run `python manage.py axes_reset`.
- **Password recovery:** in local DEBUG mode, the link appears in the terminal instead of email. Production needs working SMTP.
- **Cannot run Gunicorn on Windows:** use `runserver` only for local work. The Linux hosting instructions use Gunicorn.

## Tests

```powershell
.venv\Scripts\python.exe manage.py test garden
```

Tests create and destroy their own test database. They do not delete your normal garden records.
