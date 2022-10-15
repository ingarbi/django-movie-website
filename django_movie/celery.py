import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_movie.settings')

app = Celery('django_movie')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()