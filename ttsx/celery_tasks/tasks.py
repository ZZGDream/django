# 加密用户编号
from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from celery import Celery
from django.conf import settings
import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE',"ttsx.settings")

app=Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/6')
django.setup()


app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/6')


@app.task
def send_user_active(user_id,email):
    serializer = Serializer(settings.SECRET_KEY, 60 * 60 * 24 * 7)
    # 加密后为二进制类型应该进行解码成字符串
    value = serializer.dumps({'id': user_id}).decode()
    msg = "<a href='http://127.0.0.1:8000/user/active/%s'>点击激活</a>" % value
    send_mail('天天生鲜-账户激活', '', settings.EMAIL_FROM, [email], html_message=msg)
