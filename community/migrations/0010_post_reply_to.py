# Generated by Django 5.1.4 on 2025-01-11 17:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0009_alter_reaction_reaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='community.post'),
        ),
    ]
