import json
from pathlib import Path
from .models import LANGUAGES
LABELS=json.loads((Path(__file__).parent/'labels.json').read_text(encoding='utf-8'))
def site_context(request):
    lang=getattr(request,'garden_language','en')
    return {'lang':lang,'languages':LANGUAGES,'ui':{**LABELS['en'],**LABELS.get(lang,{})}}
