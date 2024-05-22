# Generated by Django 4.2.7 on 2024-01-25 13:22

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("analysis", "0005_remove_simulationenviroment_analysis_and_more"),
        ("api_gateway", "0002_populate_database"),
    ]

    operations = [
        migrations.CreateModel(
            name="HedgeSimulation",
            fields=[
                (
                    "hedge_irr_simulation_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "fwd_rates",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.ArrayField(
                            base_field=models.FloatField(
                                validators=[
                                    django.core.validators.MinValueValidator(-10000),
                                    django.core.validators.MaxValueValidator(10000),
                                ]
                            ),
                            size=3,
                        ),
                        size=3,
                    ),
                ),
                ("response", models.JSONField(null=True)),
                (
                    "analysis",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="hedge_simulation",
                        to="analysis.analysis",
                    ),
                ),
                (
                    "simulation_environment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="analysis.simulationenviroment",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        default="6f3d8caa-ca80-4117-8d03-c487c43338bc",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="api_gateway.typestatus",
                    ),
                ),
            ],
            options={
                "db_table": "hedge_simulation",
            },
        ),
    ]
