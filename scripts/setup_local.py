"""Create development settings once; never overwrite an existing .env."""
from pathlib import Path
import secrets
root=Path(__file__).resolve().parent.parent
env=root/'.env'
if env.exists():
    print('.env already exists; left unchanged.')
else:
    env.write_text('DEBUG=true\nSECRET_KEY='+secrets.token_urlsafe(64)+'\nALLOWED_HOSTS=localhost,127.0.0.1\nSITE_URL=http://127.0.0.1:8000\nWEATHER_ENABLED=false\n',encoding='utf-8')
    try: env.chmod(0o600)
    except OSError: pass
    print('Local .env created with a unique secret. Never use DEBUG=true on public hosting.')
