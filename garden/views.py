import csv
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, IntegerField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST, require_GET
from .models import Plant, Region, Guide, GardenEntry, LANGUAGES, translated
from .forms import SignUpForm, PlannerForm, EntryForm
from .security import allowed
from .services import recommendations, weather_for

def home(request):
    return render(request,'garden/home.html',{'plants':Plant.objects.filter(published=True,slug__in=['tomato','tulsi','mint','marigold']).order_by(Case(When(slug='tulsi',then=0),When(slug='tomato',then=1),When(slug='marigold',then=2),default=3,output_field=IntegerField())),'guides':Guide.objects.filter(published=True,category='home')[:3],'regions':Region.objects.all(),'month':timezone.localdate().month})
def plants(request):
    qs=Plant.objects.filter(published=True)
    q=request.GET.get('q','').strip()[:100]
    if q:
        condition=Q(scientific_name__icontains=q)
        for lang in LANGUAGES: condition |= Q(**{f'name__{lang}__icontains':q})
        qs=qs.filter(condition)
    category=request.GET.get('category','')
    if category in dict(Plant.CATEGORIES): qs=qs.filter(category=category)
    if request.GET.get('beginner')=='1': qs=qs.filter(beginner=True)
    if request.GET.get('container')=='1': qs=qs.filter(container_friendly=True)
    return render(request,'garden/plants.html',{'page':Paginator(qs,12).get_page(request.GET.get('page')),'q':q,'categories':Plant.CATEGORIES,'category':category})
def plant_detail(request,slug):
    plant=get_object_or_404(Plant.objects.prefetch_related('sources','windows__region'),slug=slug,published=True)
    return render(request,'garden/plant_detail.html',{'plant':plant})
def planner(request):
    form=PlannerForm(request.GET or None,initial={'month':timezone.localdate().month,'space':'balcony','sunlight':5})
    matches=None; region=None; weather=None
    if form.is_bound and form.is_valid():
        region=form.cleaned_data['region']
        matches=recommendations(**form.cleaned_data)
        weather=weather_for(region)
    return render(request,'garden/planner.html',{'form':form,'matches':matches,'region':region,'weather':weather,'weather_enabled':settings.WEATHER_ENABLED})
def guides(request,category='home'):
    if category not in dict(Guide.CATEGORIES): category='home'
    return render(request,'garden/guides.html',{'guides':Guide.objects.filter(published=True,category=category),'category':category,'heading':dict(Guide.CATEGORIES)[category],'regions':Region.objects.all() if category=='soil' else []})
def guide_detail(request,slug):
    return render(request,'garden/guide_detail.html',{'guide':get_object_or_404(Guide.objects.prefetch_related('sources'),slug=slug,published=True)})
@require_POST
def language(request):
    lang=request.POST.get('language','en')
    if lang not in LANGUAGES: lang='en'
    target=request.POST.get('next','/')
    if not url_has_allowed_host_and_scheme(target,allowed_hosts={request.get_host()},require_https=request.is_secure()): target='/'
    response=redirect(target)
    response.set_cookie('garden_language',lang,max_age=31536000,secure=not settings.DEBUG,httponly=True,samesite='Lax')
    return response

def signup(request):
    form=SignUpForm(request.POST or None)
    if request.method=='POST':
        if not allowed(request,'signup',5): return render(request,'registration/locked.html',status=429)
        if form.is_valid():
            user=form.save()
            login(request,user,backend='django.contrib.auth.backends.ModelBackend')
            return redirect('my_garden')
    return render(request,'registration/form.html',{'form':form,'title':'Create your garden account','button':'Create account','signup':True})
class LimitedPasswordResetView(PasswordResetView):
    template_name='registration/form.html'
    email_template_name='registration/password_reset_email.txt'
    subject_template_name='registration/password_reset_subject.txt'
    extra_context={'title':'Reset your password','button':'Send reset link'}
    def post(self,request,*args,**kwargs):
        if not allowed(request,'password-reset',5): return render(request,'registration/locked.html',status=429)
        return super().post(request,*args,**kwargs)
@login_required
def my_garden(request):
    entries=GardenEntry.objects.filter(owner=request.user).select_related('plant')
    return render(request,'garden/my_garden.html',{'entries':entries,'today':timezone.localdate(),'growing':entries.filter(status='growing').count()})
@login_required
def entry_edit(request,pk=None):
    entry=get_object_or_404(GardenEntry,pk=pk,owner=request.user) if pk else None
    initial={'planted_on':timezone.localdate()}
    if not pk and request.GET.get('plant','').isdigit(): initial['plant']=request.GET['plant']
    form=EntryForm(request.POST or None,instance=entry,initial=initial)
    if request.method=='POST' and form.is_valid():
        obj=form.save(commit=False); obj.owner=request.user; obj.save()
        messages.success(request,'Your garden has been updated.')
        return redirect('my_garden')
    return render(request,'registration/form.html',{'form':form,'title':'Update your plant' if entry else 'Add to your garden','button':'Save plant'})
@login_required
@require_POST
def entry_delete(request,pk):
    get_object_or_404(GardenEntry,pk=pk,owner=request.user).delete()
    messages.success(request,'Plant removed from your garden.')
    return redirect('my_garden')
@login_required
def export_garden(request):
    response=HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition']='attachment; filename="my-garden.csv"'
    response.write('\ufeff')
    writer=csv.writer(response); writer.writerow(['Plant','Nickname','Planted on','Next care','Status','Notes'])
    def safe(value):
        text=str(value or '')
        return "'"+text if text.lstrip().startswith(('=','+','-','@','\t','\r','\n')) else text
    for e in GardenEntry.objects.filter(owner=request.user).select_related('plant'):
        writer.writerow([safe(v) for v in [translated(e.plant.name,request.garden_language),e.nickname,e.planted_on,e.next_care,e.status,e.notes]])
    return response
@login_required
def delete_account(request):
    form=AuthenticationForm(request,data=request.POST or None)
    if request.method=='POST' and form.is_valid() and form.get_user().pk==request.user.pk:
        request.user.delete()
        return redirect('home')
    return render(request,'registration/form.html',{'form':form,'title':'Delete your account and garden permanently','button':'Delete my account'})
def about(request):
    import json
    path=settings.BASE_DIR/'data/ASSET_CREDITS.json'
    credits=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    return render(request,'garden/about.html',{'credits':credits})
def privacy(request): return render(request,'garden/privacy.html')
@require_GET
def health(request): return JsonResponse({'status':'ok'})
def robots(request):
    return HttpResponse('User-agent: *\nDisallow: /admin/\nDisallow: /accounts/\nDisallow: /my-garden/\nSitemap: '+settings.SITE_URL+'/sitemap.xml\n',content_type='text/plain')
