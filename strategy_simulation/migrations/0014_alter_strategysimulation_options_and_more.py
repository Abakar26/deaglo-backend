# Generated by Django 4.2.7 on 2024-02-02 16:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("strategy_simulation", "0013_populate_strategy_leg"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="strategysimulation",
            options={"ordering": ["pin", "-date_updated"]},
        ),
        migrations.AddField(
            model_name="strategysimulation",
            name="pin",
            field=models.BooleanField(default=False),
        ),
    ]
