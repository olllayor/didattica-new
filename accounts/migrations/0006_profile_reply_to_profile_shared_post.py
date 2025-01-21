# Generated by Django 5.1.4 on 2025-01-11 16:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_followers_profile_following'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='shared_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shares', to='accounts.profile'),
        ),
    ]
