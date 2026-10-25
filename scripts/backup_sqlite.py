"""Consistent SQLite backup. Destination must be OUTSIDE the web-served directory."""
import argparse,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('destination');a=p.parse_args()
source=Path(__file__).resolve().parent.parent/'db.sqlite3'
destination=Path(a.destination).resolve()
if not source.exists():raise SystemExit('No SQLite database found.')
if destination.exists() or destination==source.resolve():raise SystemExit('Choose a new backup file; existing files are never overwritten.')
destination.parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(source) as src,sqlite3.connect(destination) as dst:src.backup(dst)
try:destination.chmod(0o600)
except OSError:pass
print('Backup written. Store securely and test restoration.')
