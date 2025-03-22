import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    cmd = 'pkill -f "celery worker"'
    subprocess.call(shlex.split(cmd))
    cmd = "celery -A flash_promo worker --beat --scheduler django -l INFO --concurrency 1 -Q celery,long"
    subprocess.call(shlex.split(cmd), stdout=subprocess.PIPE)


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting celery worker with autoreload...")

        autoreload.run_with_reloader(restart_celery)
