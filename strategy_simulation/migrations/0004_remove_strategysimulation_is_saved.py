# Generated by Django 4.2.7 on 2023-12-20 02:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("strategy_simulation", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="strategysimulation",
            name="is_saved",
        ),
    ]
