from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import io, uuid
LANGUAGES = {'en':'English','hi':'हिन्दी','mr':'मराठी','ta':'தமிழ்','bn':'বাংলা'}
def translated(value, language='en'):
    return (value.get(language) or value.get('en','')) if isinstance(value,dict) else str(value or '')
def validate_translations(value):
    if not isinstance(value,dict) or not value.get('en') or any(k not in LANGUAGES or not isinstance(v,str) for k,v in value.items()):
        raise ValidationError('Use a JSON object with an English (en) value and optional hi, mr, ta, bn text values.')
def validate_months(value):
    if not isinstance(value,list) or not value or any(type(m) is not int or not 1 <= m <= 12 for m in value):
        raise ValidationError('Supply a non-empty list of month numbers, e.g. [6, 7, 8].')
def validate_photo(file):
    if file.size > 3*1024*1024:
        raise ValidationError('Maximum photograph size is 3 MB.')
    try:
        img = Image.open(file)
        if img.format not in {'JPEG','PNG','WEBP'} or img.width*img.height > 16000000:
            raise ValidationError('Use JPEG, PNG or WebP, at most 16 megapixels.')
        img.verify()
    except (OSError,Image.DecompressionBombError) as exc:
        raise ValidationError('Invalid image.') from exc
    finally:
        file.seek(0)
class Source(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    notes = models.TextField(blank=True)
    def __str__(self): return self.title
class Plant(models.Model):
    CATEGORIES = [('vegetable','Vegetables'),('herb','Herbs'),('flower','Flowers'),('indoor','Indoor plants'),('fruit','Fruit')]
    slug = models.SlugField(unique=True)
    name = models.JSONField(validators=[validate_translations])
    scientific_name = models.CharField(max_length=150)
    category = models.CharField(max_length=20,choices=CATEGORIES)
    summary = models.JSONField(validators=[validate_translations])
    care = models.JSONField(validators=[validate_translations])
    soil = models.JSONField(validators=[validate_translations])
    photo = models.ImageField(upload_to='plants/%Y/%m/',blank=True,validators=[validate_photo])
    image_file = models.CharField(max_length=100,default='garden/images/garden.jpg',help_text='Bundled static photo path; trusted administrator only.')
    image_credit = models.CharField(max_length=250,blank=True)
    image_source = models.URLField(blank=True,max_length=500)
    image_license = models.CharField(max_length=150,blank=True)
    image_license_url = models.URLField(blank=True,max_length=500)
    min_sun = models.PositiveSmallIntegerField(default=4,validators=[MaxValueValidator(12)])
    container_cm = models.PositiveSmallIntegerField(default=25,validators=[MinValueValidator(5),MaxValueValidator(200)])
    container_friendly = models.BooleanField(default=True)
    beginner = models.BooleanField(default=True)
    harvest_days = models.CharField(max_length=50,blank=True)
    caution = models.JSONField(default=dict,blank=True)
    sources = models.ManyToManyField(Source,blank=True)
    published = models.BooleanField(default=True)
    reviewed_on = models.DateField(null=True,blank=True)
    translation_reviewed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['slug']
    def save(self,*args,**kwargs):
        if self.photo and not self.photo._committed:
            validate_photo(self.photo)
            img=ImageOps.exif_transpose(Image.open(self.photo)).convert('RGB')
            img.thumbnail((1600,1600))
            output=io.BytesIO(); img.save(output,format='JPEG',quality=88)
            self.photo.save(uuid.uuid4().hex+'.jpg',ContentFile(output.getvalue()),save=False)
        super().save(*args,**kwargs)
    def __str__(self): return translated(self.name)
    def get_absolute_url(self): return reverse('plant_detail',args=[self.slug])
class Region(models.Model):
    slug = models.SlugField(unique=True)
    name = models.JSONField(validators=[validate_translations])
    state = models.CharField(max_length=100)
    climate = models.JSONField(validators=[validate_translations])
    soil_notes = models.JSONField(validators=[validate_translations])
    latitude = models.FloatField(validators=[MinValueValidator(-90),MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180),MaxValueValidator(180)])
    class Meta: ordering = ['state','slug']
    def __str__(self): return translated(self.name)
class PlantingWindow(models.Model):
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,related_name='windows')
    region = models.ForeignKey(Region,on_delete=models.CASCADE,related_name='windows')
    months = models.JSONField(validators=[validate_months])
    action = models.CharField(max_length=15,choices=[('sow','Sow seeds'),('transplant','Transplant'),('plant','Plant')],default='sow')
    notes = models.JSONField(validators=[validate_translations])
    source = models.ForeignKey(Source,on_delete=models.PROTECT)
    verified = models.BooleanField(default=False,help_text='Mark only after review for this region, variety and action.')
    class Meta:
        constraints = [models.UniqueConstraint(fields=['plant','region','action'],name='unique_plant_region_action')]
class Guide(models.Model):
    CATEGORIES = [('home','Home gardening'),('soil','Soil & climate'),('equipment','Tools & equipment'),('diary','Garden diaries')]
    slug = models.SlugField(unique=True)
    title = models.JSONField(validators=[validate_translations])
    summary = models.JSONField(validators=[validate_translations])
    body = models.JSONField(validators=[validate_translations])
    category = models.CharField(max_length=15,choices=CATEGORIES)
    image_file = models.CharField(max_length=100,default='garden/images/garden.jpg')
    sources = models.ManyToManyField(Source,blank=True)
    published = models.BooleanField(default=True)
    translation_reviewed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return translated(self.title)
    def get_absolute_url(self): return reverse('guide_detail',args=[self.slug])
class GardenEntry(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant,on_delete=models.PROTECT)
    nickname = models.CharField(max_length=80,blank=True)
    planted_on = models.DateField()
    next_care = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=12,choices=[('planned','Planned'),('growing','Growing'),('harvested','Harvested'),('archived','Archived')],default='planned')
    notes = models.TextField(max_length=3000,blank=True)
    class Meta: ordering = ['next_care','-id']
class RequestBucket(models.Model):
    key = models.CharField(max_length=64,unique=True)
    count = models.PositiveIntegerField(default=0)
    expires = models.DateTimeField()
