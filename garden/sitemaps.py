from django.contrib.sitemaps import Sitemap
from .models import Plant, Guide
class PlantSitemap(Sitemap):
    changefreq='monthly'
    def items(self): return Plant.objects.filter(published=True)
    def lastmod(self,obj): return obj.updated_at
class GuideSitemap(Sitemap):
    changefreq='monthly'
    def items(self): return Guide.objects.filter(published=True).order_by('slug')
    def lastmod(self,obj): return obj.updated_at
