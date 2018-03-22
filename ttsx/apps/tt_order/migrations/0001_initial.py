# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('add_date', models.DateField(auto_now_add=True)),
                ('update_date', models.DateField(auto_now=True)),
                ('isDelete', models.BooleanField(default=False)),
                ('count', models.IntegerField(default=1, verbose_name='数量')),
                ('price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')),
                ('comment', models.TextField(default='', verbose_name='评价信息')),
            ],
            options={
                'db_table': 'df_order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('add_date', models.DateField(auto_now_add=True)),
                ('update_date', models.DateField(auto_now=True)),
                ('isDelete', models.BooleanField(default=False)),
                ('order_id', models.CharField(max_length=64, serialize=False, primary_key=True, verbose_name='订单号')),
                ('total_count', models.IntegerField(default=1, verbose_name='商品总数')),
                ('total_amount', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总金额')),
                ('trans_cost', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')),
                ('pay_method', models.SmallIntegerField(default=1, choices=[(1, '货到付款'), (2, '支付宝')], verbose_name='支付方式')),
                ('status', models.SmallIntegerField(default=1, choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], verbose_name='订单状态')),
                ('trade_id', models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name='支付编号')),
            ],
            options={
                'db_table': 'df_order_info',
            },
        ),
    ]
