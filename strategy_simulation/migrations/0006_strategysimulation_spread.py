# Generated by Django 4.2.7 on 2023-12-29 00:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("strategy_simulation", "0005_strategysimulation_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="strategysimulation",
            name="spread",
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]
