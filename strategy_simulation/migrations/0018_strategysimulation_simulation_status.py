# Generated by Django 4.2.7 on 2024-02-21 21:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("strategy_simulation", "0017_populate_strategy"),
    ]

    operations = [
        migrations.AddField(
            model_name="strategysimulation",
            name="simulation_status",
            field=models.CharField(
                choices=[
                    ("ENQUEUED", "ENQUEUED"),
                    ("IN PROGRESS", "IN PROGRESS"),
                    ("COMPLETED", "COMPLETED"),
                    ("FAILED", "FAILED"),
                ],
                default="ENQUEUED",
            ),
        ),
    ]
