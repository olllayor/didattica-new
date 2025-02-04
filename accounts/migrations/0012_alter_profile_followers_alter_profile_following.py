# Generated by Django 5.1.4 on 2025-01-16 15:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0011_remove_profile_telegraph_profile_url"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="followers",
            field=models.ManyToManyField(
                blank=True,
                related_name="following_profiles",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="following",
            field=models.ManyToManyField(
                blank=True,
                related_name="follower_profiles",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
