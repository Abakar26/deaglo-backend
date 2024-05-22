# Generated by Django 4.2.7 on 2024-02-09 12:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("api_gateway", "0003_alter_typecurrency_options"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("analysis", "0006_alter_analysis_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Workspace",
            fields=[
                (
                    "workspace_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "analysis",
                    models.ManyToManyField(
                        blank=True, related_name="workspace", to="analysis.analysis"
                    ),
                ),
                (
                    "base_currency",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="workspace_base_currency_set",
                        to="api_gateway.typecurrency",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="workspaces",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "workspace",
                "ordering": ("-date_updated", "-date_added"),
            },
        ),
    ]