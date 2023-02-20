from celery import shared_task
from django.core.mail import send_mail


@shared_task()
def send_email(email_address, message):
    send_mail("Информация", message, "dayana@host", email_address)