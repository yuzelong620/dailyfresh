from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
# import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
# django.setup()
#实例化Celery对象
app = Celery('celery_tasks.tasks',broker='redis://62.234.142.229:6379/4')


@app.task
def send_register_active_email(to_email, username, token):
    # 给用户发验证邮件
    subject = '邮箱验证'
    message = '<h1>%s, 请验证邮箱</h1><br/><br/>请点击链接激活账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 请验证邮箱</h1><br/><br/>请点击链接激活账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    send_mail(subject, '', sender, receiver, html_message=html_message)