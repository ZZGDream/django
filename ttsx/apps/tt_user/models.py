from django.db import models
from utils.models import BaseModel
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(BaseModel, AbstractUser):
    class Meta:
        db_table = 'df_user'


class AreaInfo(models.Model):
    title = models.CharField(max_length=20)
    aparent = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        db_table = 'da_area'


class Address(models.Model):
    receiver = models.CharField(max_length=20)
    province = models.ForeignKey(AreaInfo, related_name='province')
    city = models.ForeignKey(AreaInfo, related_name='city')
    distirct = models.ForeignKey(AreaInfo, related_name='district')
    addr = models.CharField(max_length=100)
    code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=11)
    #是否默认地址
    isDefault = models.BooleanField(default=False)

    class Meta:
        db_table = 'df_address'
