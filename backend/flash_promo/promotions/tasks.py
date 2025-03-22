from celery import shared_task


@shared_task
def send_user_notification(*args, **kwargs):
    pass
