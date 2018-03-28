# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tt_user', '0003_address_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='distirct',
            new_name='district',
        ),
    ]
