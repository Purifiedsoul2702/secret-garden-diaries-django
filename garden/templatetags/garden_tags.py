from django import template
from django.templatetags.static import static
from garden.models import translated
import calendar
register=template.Library()
@register.filter
def tr(value,language): return translated(value,language)
@register.filter
def missing(value,language): return isinstance(value,dict) and not value.get(language)
@register.simple_tag
def photo(plant): return plant.photo.url if plant.photo else static(plant.image_file)
@register.filter
def months(values): return ', '.join(calendar.month_abbr[int(v)] for v in values)
@register.simple_tag(takes_context=True)
def query_page(context,num):
    query=context['request'].GET.copy(); query['page']=num
    return '?'+query.urlencode()
