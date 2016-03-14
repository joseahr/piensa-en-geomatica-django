# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('radiacion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='shp',
            field=models.FileField(default=datetime.datetime(2016, 3, 10, 22, 26, 44, 87379, tzinfo=utc), upload_to=b''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='docfile',
            field=models.FileField(upload_to=b''),
            preserve_default=True,
        ),
    ]
