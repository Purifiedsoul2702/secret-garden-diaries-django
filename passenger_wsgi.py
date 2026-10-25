"""cPanel/Passenger entry point. Configure the correct virtualenv in the hosting panel."""
import os, sys
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
from django.core.wsgi import get_wsgi_application
application=get_wsgi_application()
