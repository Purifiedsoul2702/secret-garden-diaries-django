import io
from datetime import date
from unittest.mock import patch
from django.test import TestCase, Client, override_settings, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from .models import Plant, Region, Guide, GardenEntry, validate_months, validate_photo, translated
from .services import recommendations,weather_for
from .security import client_ip
FAST={'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache'}}
STORAGE={'default':{'BACKEND':'django.core.files.storage.InMemoryStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}}
@override_settings(CACHES=FAST,STORAGES=STORAGE,DEBUG=True,SECURE_SSL_REDIRECT=False,ALLOWED_HOSTS=['testserver'],PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class GardenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_garden',verbosity=0)
        cls.user=User.objects.create_user('gardener','grow@example.com','A-long-green-password!')
        cls.other=User.objects.create_user('neighbour','other@example.com','Another-long-password!')
        cls.plant=Plant.objects.get(slug='tomato')
        cls.region=Region.objects.get(slug='pune')
    def test_seed_is_idempotent(self):
        self.plant.summary={'en':'Edited by owner'};self.plant.save()
        call_command('seed_garden',verbosity=0)
        self.plant.refresh_from_db()
        self.assertEqual(Plant.objects.count(),12);self.assertEqual(self.plant.summary['en'],'Edited by owner')
    def test_public_routes(self):
        for url in ['/','/plants/','/planner/','/soil/','/home-gardening/','/equipment/','/diaries/','/about/','/privacy/','/health/','/sitemap.xml','/robots.txt']:
            with self.subTest(url=url): self.assertEqual(self.client.get(url).status_code,200)
    def test_all_detail_pages(self):
        for obj in list(Plant.objects.all())+list(Guide.objects.all()):
            self.assertEqual(self.client.get(obj.get_absolute_url()).status_code,200)
    def test_five_languages(self):
        for lang in ['en','hi','mr','ta','bn']:
            self.client.cookies['garden_language']=lang
            r=self.client.get(self.plant.get_absolute_url())
            self.assertContains(r,self.plant.name[lang]);self.assertContains(r,f'lang="{lang}"')
    def test_invalid_language_cookie_falls_back(self):
        self.client.cookies['garden_language']='evil';self.assertContains(self.client.get('/'),'lang="en"')
    def test_language_switch_post_only(self): self.assertEqual(self.client.get('/language/').status_code,405)
    def test_language_open_redirect_blocked(self):
        r=self.client.post('/language/',{'language':'mr','next':'https://evil.example/'})
        self.assertEqual(r.url,'/');self.assertEqual(r.cookies['garden_language'].value,'mr')
    def test_csrf_required(self):
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.post('/language/',{'language':'mr'}).status_code,403)
        self.assertEqual(c.post('/accounts/signup/',{}).status_code,403)
    def test_multilingual_search(self):
        self.assertContains(self.client.get('/plants/',{'q':'टोमॅटो'}),'Tomato')
        self.assertContains(self.client.get('/plants/',{'q':'Solanum'}),'Tomato')
    def test_category_filter(self):
        r=self.client.get('/plants/',{'category':'herb'})
        self.assertContains(r,'Coriander');self.assertNotContains(r,'Solanum lycopersicum')
    def test_unpublished_plant_hidden(self):
        self.plant.published=False;self.plant.save()
        self.assertEqual(self.client.get(self.plant.get_absolute_url()).status_code,404)
    def test_unpublished_guide_hidden(self):
        g=Guide.objects.first();g.published=False;g.save()
        self.assertEqual(self.client.get(g.get_absolute_url()).status_code,404)
    def test_planner_filters_month_sun_and_space(self):
        matches=recommendations(self.region,10,'balcony',5)
        self.assertTrue(matches)
        self.assertTrue(all(10 in w.months and w.plant.min_sun<=5 and w.plant.container_friendly for w in matches))
        self.assertTrue(all(w.plant.category=='indoor' for w in recommendations(self.region,10,'indoor',5)))
    def test_invalid_planner_input(self):
        r=self.client.get('/planner/',{'region':self.region.pk,'month':99,'space':'balcony','sunlight':5})
        self.assertEqual(r.status_code,200);self.assertFalse(r.context['form'].is_valid())
    def test_successful_planner_page(self):
        r=self.client.get('/planner/',{'region':self.region.pk,'month':10,'space':'balcony','sunlight':5})
        self.assertEqual(r.status_code,200);self.assertGreater(len(r.context['matches']),0)
    def test_no_unsupported_region_guess(self):
        r=self.client.get('/planner/',{'region':9999,'month':10,'space':'balcony','sunlight':5})
        self.assertFalse(r.context['form'].is_valid())
    def test_security_headers(self):
        r=self.client.get('/')
        self.assertIn("script-src 'self'",r['Content-Security-Policy'])
        self.assertEqual(r['X-Frame-Options'],'DENY');self.assertEqual(r['X-Content-Type-Options'],'nosniff')
    def test_private_pages_require_login(self):
        for url in ['/my-garden/','/my-garden/add/','/my-garden/export/']:
            self.assertEqual(self.client.get(url).status_code,302)
    def make_entry(self):
        return GardenEntry.objects.create(owner=self.user,plant=self.plant,planted_on=date.today(),notes='<script>alert(1)</script>')
    def test_owner_isolation(self):
        e=self.make_entry();self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/my-garden/{e.pk}/edit/').status_code,404)
        self.assertEqual(self.client.post(f'/my-garden/{e.pk}/delete/').status_code,404)
        self.assertNotContains(self.client.get('/my-garden/export/'),'alert(1)')
    def test_journal_xss_escaped(self):
        self.make_entry();self.client.force_login(self.user)
        r=self.client.get('/my-garden/')
        self.assertContains(r,'&lt;script&gt;');self.assertNotContains(r,'<script>alert(1)</script>')
        self.assertEqual(r['Cache-Control'],'private, no-store')
    def test_delete_requires_post(self):
        e=self.make_entry();self.client.force_login(self.user)
        self.assertEqual(self.client.get(f'/my-garden/{e.pk}/delete/').status_code,405)
        self.assertEqual(self.client.post(f'/my-garden/{e.pk}/delete/').status_code,302)
        self.assertFalse(GardenEntry.objects.filter(pk=e.pk).exists())
    def test_create_ignores_forged_owner(self):
        self.client.force_login(self.user)
        r=self.client.post('/my-garden/add/',{'plant':self.plant.pk,'planted_on':'2026-10-01','status':'growing','owner':self.other.pk,'notes':'Hello'})
        self.assertEqual(r.status_code,302);self.assertEqual(GardenEntry.objects.get().owner,self.user)
    def test_invalid_care_date(self):
        self.client.force_login(self.user)
        r=self.client.post('/my-garden/add/',{'plant':self.plant.pk,'planted_on':'2026-10-02','next_care':'2026-10-01','status':'growing'})
        self.assertEqual(r.status_code,200);self.assertEqual(GardenEntry.objects.count(),0)
    def test_csv_formula_protection(self):
        e=self.make_entry();e.nickname='=1+1';e.save();self.client.force_login(self.user)
        self.assertIn("'=1+1",self.client.get('/my-garden/export/').content.decode())
    def test_signup_and_weak_password(self):
        r=self.client.post('/accounts/signup/',{'username':'newuser','email':'new@example.com','password1':'short','password2':'short'})
        self.assertEqual(r.status_code,200);self.assertFalse(User.objects.filter(username='newuser').exists())
        r=self.client.post('/accounts/signup/',{'username':'newuser','email':'new@example.com','password1':'River!Bloom-8912','password2':'River!Bloom-8912'})
        self.assertEqual(r.status_code,302);self.assertTrue(User.objects.get(username='newuser').check_password('River!Bloom-8912'))
    def test_signup_throttle(self):
        for _ in range(5):self.client.post('/accounts/signup/',{})
        self.assertEqual(self.client.post('/accounts/signup/',{}).status_code,429)
    def test_password_reset_throttle(self):
        for _ in range(5):self.client.post('/accounts/password-reset/',{'email':'nobody@example.com'})
        self.assertEqual(self.client.post('/accounts/password-reset/',{'email':'nobody@example.com'}).status_code,429)
    def test_login_lockout(self):
        for _ in range(5):self.client.post('/accounts/login/',{'username':'gardener','password':'wrong'})
        self.assertEqual(self.client.post('/accounts/login/',{'username':'gardener','password':'A-long-green-password!'}).status_code,429)
    def test_admin_requires_staff(self):
        self.client.force_login(self.user);self.assertEqual(self.client.get('/admin/').status_code,302)
    def test_logout_post_only(self):
        self.client.force_login(self.user);self.assertEqual(self.client.get('/accounts/logout/').status_code,405)
    def test_month_validation(self):
        for bad in [[],[0],[13],['1'],[True],'January']:
            with self.assertRaises(ValidationError):validate_months(bad)
    def test_malicious_image_rejected(self):
        with self.assertRaises(ValidationError):validate_photo(SimpleUploadedFile('bad.svg',b'<svg><script>alert(1)</script></svg>'))
    def test_image_is_sanitized(self):
        buf=io.BytesIO();Image.new('RGB',(10,10)).save(buf,format='PNG')
        self.plant.photo=SimpleUploadedFile('unsafe.html',buf.getvalue(),content_type='image/png');self.plant.save()
        self.assertTrue(self.plant.photo.name.endswith('.jpg'));self.assertNotIn('unsafe',self.plant.photo.name)
    def test_weather_disabled_no_network(self):
        with override_settings(WEATHER_ENABLED=False),patch('garden.services.urlopen') as mock:
            self.assertIsNone(weather_for(self.region));mock.assert_not_called()
    def test_weather_failure_is_graceful(self):
        from urllib.error import URLError
        from django.core.cache import cache
        cache.clear()
        with override_settings(WEATHER_ENABLED=True),patch('garden.services.urlopen',side_effect=URLError('offline')):
            self.assertIsNone(weather_for(self.region))
    def test_weather_cached(self):
        from django.core.cache import cache
        cache.clear()
        with override_settings(WEATHER_ENABLED=True),patch('garden.services.urlopen') as mock:
            mock.return_value.__enter__.return_value.read.return_value=b'{"current":{"temperature_2m":27},"daily":{"precipitation_probability_max":[40]}}'
            self.assertEqual(weather_for(self.region)['rain'],40);weather_for(self.region)
            self.assertEqual(mock.call_count,1)
    def test_forged_proxy_header_ignored(self):
        request=RequestFactory().get('/',HTTP_X_REAL_IP='1.2.3.4',REMOTE_ADDR='5.6.7.8')
        with override_settings(TRUSTED_PROXY_IPS=[]):self.assertEqual(client_ip(request),'5.6.7.8')
    def test_account_delete_requires_own_credentials(self):
        self.make_entry();self.client.force_login(self.user)
        r=self.client.post('/accounts/delete/',{'username':'neighbour','password':'Another-long-password!'})
        self.assertEqual(r.status_code,200);self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        r=self.client.post('/accounts/delete/',{'username':'gardener','password':'A-long-green-password!'})
        self.assertEqual(r.status_code,302);self.assertFalse(GardenEntry.objects.filter(owner_id=self.user.pk).exists())

    def test_password_reset_flow(self):
        import re
        from django.core import mail
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            r=self.client.post('/accounts/password-reset/',{'email':'grow@example.com'})
            self.assertEqual(r.status_code,302)
            self.assertEqual(len(mail.outbox),1)
            path=re.search(r'http://testserver(/accounts/reset/[^\s]+)',mail.outbox[0].body).group(1)
            r=self.client.get(path)
            self.assertEqual(r.status_code,302)
            r=self.client.post(r.url,{'new_password1':'Fresh-Garden-991!','new_password2':'Fresh-Garden-991!'})
            self.assertEqual(r.status_code,302)
            self.user.refresh_from_db();self.assertTrue(self.user.check_password('Fresh-Garden-991!'))
    def test_all_seed_assets_exist(self):
        from pathlib import Path
        from django.conf import settings
        import json
        credits=json.loads((settings.BASE_DIR/'data/ASSET_CREDITS.json').read_text())
        for plant in Plant.objects.all():
            self.assertTrue((settings.BASE_DIR/'static'/plant.image_file).is_file())
            self.assertIn(plant.slug,credits)
            self.assertTrue(credits[plant.slug]['license'])
    def test_private_mutation_csrf(self):
        e=self.make_entry();c=Client(enforce_csrf_checks=True);c.force_login(self.user)
        self.assertEqual(c.post(f'/my-garden/{e.pk}/delete/').status_code,403)
        self.assertTrue(GardenEntry.objects.filter(pk=e.pk).exists())
    def test_trusted_proxy_accepts_validated_real_ip(self):
        request=RequestFactory().get('/',HTTP_X_REAL_IP='1.2.3.4',REMOTE_ADDR='127.0.0.1')
        with override_settings(TRUSTED_PROXY_IPS=['127.0.0.1']):
            self.assertEqual(client_ip(request),'1.2.3.4')
            request.META['HTTP_X_REAL_IP']='not-an-ip';self.assertEqual(client_ip(request),'127.0.0.1')
