# Generated by Django 4.2.7 on 2024-01-25 19:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("hedge_simulation", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="hedgesimulation",
            name="result_id",
            field=models.UUIDField(auto_created=True, default=uuid.uuid4),
        ),
    ]
