import hashlib
import ipaddress
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import RequestBucket
def client_ip(request):
    # Never trust client-supplied X-Forwarded-For headers.
    peer = request.META.get('REMOTE_ADDR','unknown')
    if peer in settings.TRUSTED_PROXY_IPS:
        try: return str(ipaddress.ip_address(request.META.get('HTTP_X_REAL_IP','')))
        except ValueError: pass
    return peer
def allowed(request, scope, limit=10, seconds=3600):
    now = timezone.now()
    key = hashlib.sha256(f'{settings.SECRET_KEY}:{scope}:{client_ip(request)}'.encode()).hexdigest()
    with transaction.atomic():
        bucket,_ = RequestBucket.objects.get_or_create(key=key,defaults={'expires':now+timedelta(seconds=seconds)})
        bucket = RequestBucket.objects.select_for_update().get(pk=bucket.pk)
        if bucket.expires <= now:
            bucket.count=0; bucket.expires=now+timedelta(seconds=seconds)
        if bucket.count >= limit: return False
        bucket.count += 1; bucket.save(update_fields=['count','expires'])
    return True
