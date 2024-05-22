# Generated by Django 4.2.7 on 2024-01-12 02:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0001_initial"),
        ("analysis", "0003_alter_analysis_base_currency_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="analysis",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="analysis",
                to="organization.organization",
            ),
        ),
    ]