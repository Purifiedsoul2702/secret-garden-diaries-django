import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import PlantingWindow

def recommendations(region,month,space,sunlight):
    windows=PlantingWindow.objects.filter(region=region,plant__published=True).select_related('plant','source')
    results=[]
    for w in windows:
        if month not in w.months or w.plant.min_sun > sunlight: continue
        if space in {'balcony','terrace'} and not w.plant.container_friendly: continue
        if space == 'indoor' and w.plant.category != 'indoor': continue
        results.append(w)
    return results

def weather_for(region):
    if not settings.WEATHER_ENABLED: return None
    key=f'weather:{region.pk}'
    cached=cache.get(key)
    if cached is not None: return cached or None
    # Region coordinates are curated by staff. No user-supplied URL, key or remote host.
    url=f'https://api.open-meteo.com/v1/forecast?latitude={region.latitude}&longitude={region.longitude}&current=temperature_2m&daily=precipitation_probability_max&forecast_days=1&timezone=Asia%2FKolkata'
    try:
        with urlopen(Request(url,headers={'User-Agent':'SecretGardenDiaries/1.0'}),timeout=4) as response:
            raw=response.read(100001)
        if len(raw)>100000: raise ValueError('Response too large')
        data=json.loads(raw)
        result={'temperature':float(data['current']['temperature_2m']),'rain':int(data['daily']['precipitation_probability_max'][0]),'fetched':timezone.now().isoformat()}
        cache.set(key,result,1800)
        return result
    except (URLError,TimeoutError,ValueError,KeyError,IndexError,TypeError,OSError):
        cache.set(key,{},300)
        return None
