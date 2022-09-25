# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('final_year', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='backup_db',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price_now', models.TextField(null=True)),
                ('coin_overall_data', models.TextField(null=True)),
            ],
        ),
    ]
