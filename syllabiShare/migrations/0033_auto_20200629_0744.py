# Generated by Django 3.0.7 on 2020-06-29 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('syllabiShare', '0032_userprofile_confirmations_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='hide_name',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='submission',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
