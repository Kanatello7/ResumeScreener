# Generated by Django 5.1.6 on 2025-03-01 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='details',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
