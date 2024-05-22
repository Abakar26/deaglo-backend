# Generated by Django 4.2.7 on 2024-01-09 01:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("strategy_simulation", "0006_strategysimulation_spread"),
    ]

    operations = [
        migrations.CreateModel(
            name="Strategy",
            fields=[
                (
                    "strategy_id",
                    models.UUIDField(
                        auto_created=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=100)),
                ("description", models.CharField(max_length=300)),
                ("sort_order", models.IntegerField(blank=True, null=True)),
                ("image_url", models.CharField(blank=True, max_length=250, null=True)),
                (
                    "created_by_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "strategy",
            },
        ),
        migrations.RemoveField(
            model_name="strategyinstance",
            name="custom_strategy_leg",
        ),
        migrations.RemoveField(
            model_name="strategyinstance",
            name="type_default_strategy_leg",
        ),
        migrations.CreateModel(
            name="StrategyLeg",
            fields=[
                (
                    "strategy_leg_id",
                    models.UUIDField(
                        auto_created=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("sort_order", models.IntegerField(blank=True, null=True)),
                ("image_url", models.CharField(blank=True, max_length=255, null=True)),
                ("is_call", models.BooleanField(blank=True, null=True)),
                ("is_bought", models.BooleanField()),
                ("premium", models.DecimalField(decimal_places=2, max_digits=1000)),
                ("leverage", models.FloatField()),
                ("strike", models.FloatField(blank=True, null=True)),
                ("barrier_type", models.CharField(blank=True, max_length=8, null=True)),
                ("barrier_level", models.FloatField(blank=True, null=True)),
                (
                    "strategy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="strategy_leg",
                        to="strategy_simulation.strategy",
                    ),
                ),
            ],
            options={
                "db_table": "strategy_leg",
            },
        ),
        migrations.AddField(
            model_name="strategyinstance",
            name="strategy_leg",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="strategy_simulation.strategyleg",
            ),
        ),
    ]
