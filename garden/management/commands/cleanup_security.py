from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from axes.models import AccessAttempt, AccessLog
from garden.models import RequestBucket
class Command(BaseCommand):
    help='Delete expired rate-limit records and login records older than seven days. Run daily.'
    def handle(self,*args,**kwargs):
        now=timezone.now()
        RequestBucket.objects.filter(expires__lt=now).delete()
        AccessAttempt.objects.filter(attempt_time__lt=now-timedelta(days=7)).delete()
        AccessLog.objects.filter(attempt_time__lt=now-timedelta(days=7)).delete()
        self.stdout.write('Expired security records removed.')
