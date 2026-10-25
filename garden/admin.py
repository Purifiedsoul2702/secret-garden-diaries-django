from django.contrib import admin
from .models import Plant, Region, PlantingWindow, Guide, Source, GardenEntry
admin.site.site_header='Secret Garden Diaries • Studio'
admin.site.site_title='Garden Studio'
admin.site.index_title='Grow your knowledge library'
class WindowInline(admin.TabularInline):
    model=PlantingWindow
    extra=0
@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display=('__str__','category','published','translation_reviewed','reviewed_on')
    list_filter=('category','published','translation_reviewed')
    search_fields=('slug','scientific_name')
    inlines=[WindowInline]
    filter_horizontal=('sources',)
@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display=('__str__','category','published','translation_reviewed')
    list_filter=('category','published')
    search_fields=('slug',)
    filter_horizontal=('sources',)
admin.site.register(Region)
admin.site.register(Source)
admin.site.register(PlantingWindow)
# Private user journals are deliberately not registered in admin.
