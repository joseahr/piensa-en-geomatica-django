# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('radiacion', '0002_auto_20160310_2226'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='fecha',
            field=models.DateTimeField(default=datetime.datetime.now, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='nombre_original',
            field=models.TextField(default=datetime.datetime(2016, 3, 12, 16, 32, 1, 104564, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='docfile',
            field=models.FileField(upload_to='radiaciones'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='shp',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
