import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from garden.models import Source,Plant,Region,PlantingWindow,Guide
class Command(BaseCommand):
    help='Add starter content without overwriting existing editorial records. No default users or passwords.'
    @transaction.atomic
    def handle(self,*args,**options):
        data=json.loads((settings.BASE_DIR/'data/starter.json').read_text(encoding='utf-8'))
        asset_path=settings.BASE_DIR/'data/ASSET_CREDITS.json'
        assets=json.loads(asset_path.read_text(encoding='utf-8')) if asset_path.exists() else {}
        sources={}
        for row in data['sources']:
            code=row.pop('id'); obj,_=Source.objects.get_or_create(url=row['url'],defaults=row); sources[code]=obj
        plants={}; regions={}
        for row in data['plants']:
            a=assets.get(row['slug'],{})
            row.update(image_credit=a.get('author','See asset credits'),image_source=a.get('source',''),image_license=a.get('license',''),image_license_url=a.get('license_url',''))
            obj,created=Plant.objects.get_or_create(slug=row['slug'],defaults=row)
            if created:
                obj.full_clean(); obj.sources.set([sources['tnau'],sources['icar']])
            plants[row['slug']]=obj
        for row in data['regions']:
            obj,_=Region.objects.get_or_create(slug=row['slug'],defaults=row); obj.full_clean(); regions[row['slug']]=obj
        for row in data['windows']:
            plant=plants[row.pop('plant')]; region=regions[row.pop('region')]; row['source']=sources[row['source']]
            obj,_=PlantingWindow.objects.get_or_create(plant=plant,region=region,action=row['action'],defaults=row); obj.full_clean()
        for row in data['guides']:
            obj,created=Guide.objects.get_or_create(slug=row['slug'],defaults=row)
            if created: obj.full_clean(); obj.sources.set([sources['tnau'],sources['icar']])
        self.stdout.write(self.style.SUCCESS(f'Content ready: {len(plants)} plants, {len(regions)} regions, {len(data["guides"])} guides. Existing content preserved.'))
