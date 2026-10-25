from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from garden import views as v
from garden.sitemaps import PlantSitemap, GuideSitemap
urlpatterns=[
 path('',v.home,name='home'),path('plants/',v.plants,name='plants'),path('plants/<slug:slug>/',v.plant_detail,name='plant_detail'),
 path('planner/',v.planner,name='planner'),path('home-gardening/',v.guides,name='guides'),path('soil/',v.guides,{'category':'soil'},name='soil'),path('equipment/',v.guides,{'category':'equipment'},name='equipment'),path('diaries/',v.guides,{'category':'diary'},name='diaries'),path('guides/<slug:slug>/',v.guide_detail,name='guide_detail'),
 path('language/',v.language,name='language'),path('about/',v.about,name='about'),path('privacy/',v.privacy,name='privacy'),
 path('accounts/signup/',v.signup,name='signup'),path('accounts/login/',auth.LoginView.as_view(template_name='registration/login.html'),name='login'),path('accounts/logout/',auth.LogoutView.as_view(),name='logout'),
 path('accounts/password-reset/',v.LimitedPasswordResetView.as_view(),name='password_reset'),path('accounts/password-reset/done/',auth.PasswordResetDoneView.as_view(template_name='registration/reset_done.html'),name='password_reset_done'),path('accounts/reset/<uidb64>/<token>/',auth.PasswordResetConfirmView.as_view(template_name='registration/form.html',extra_context={'title':'Choose a new password','button':'Save password'}),name='password_reset_confirm'),path('accounts/reset/complete/',auth.PasswordResetCompleteView.as_view(template_name='registration/reset_complete.html'),name='password_reset_complete'),path('accounts/delete/',v.delete_account,name='delete_account'),
 path('my-garden/',v.my_garden,name='my_garden'),path('my-garden/add/',v.entry_edit,name='entry_add'),path('my-garden/<int:pk>/edit/',v.entry_edit,name='entry_edit'),path('my-garden/<int:pk>/delete/',v.entry_delete,name='entry_delete'),path('my-garden/export/',v.export_garden,name='export_garden'),
 path('admin/',admin.site.urls),path('health/',v.health,name='health'),path('robots.txt',v.robots),path('sitemap.xml',sitemap,{'sitemaps':{'plants':PlantSitemap,'guides':GuideSitemap}},name='sitemap')]
if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
