# Generated by Django 4.2.7 on 2024-02-20 00:45

import authentication.models.otp
from django.conf import settings
import django.contrib.auth.validators
import django.contrib.postgres.indexes
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("organization", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "user_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                (
                    "email",
                    models.EmailField(
                        max_length=254,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator
                        ],
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        max_length=17,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                                regex="^\\+?1?\\d{9,15}$",
                            )
                        ],
                    ),
                ),
                ("city", models.CharField(max_length=255)),
                ("state", models.CharField(blank=True, max_length=100, null=True)),
                ("zip_code", models.CharField(max_length=12)),
                ("country", models.CharField(max_length=255)),
                ("company", models.CharField(max_length=255)),
                ("job_title", models.CharField(max_length=255)),
                (
                    "company_type",
                    models.CharField(
                        choices=[
                            ("BF", "Banks and Financial Institutions"),
                            ("MNC", "Multinational Corporations"),
                            ("IE", "Import/Export Businesses"),
                            ("HEDGE", "Hedge Funds"),
                            (
                                "ALT",
                                "Alternative Asset Managers (Private Equity, Credit, etc.)",
                            ),
                            ("FAM_OFF", "Family Offices / Multi-Family Offices"),
                            (
                                "INST_INV",
                                "Institutional Investors (Pension Funds, Insurance Companies, etc.)",
                            ),
                            ("SME", "SMEs with International Exposure"),
                            ("GNP", "Government and Non-Profit Organizations"),
                            ("TECH", "Technology and Software Companies"),
                            ("CONS", "Consulting and Advisory Firms"),
                            ("NGO", "Non-Governmental Organizations"),
                            ("CHAR", "Charities"),
                        ]
                    ),
                ),
                ("is_verified", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="user",
                        to="organization.organization",
                    ),
                ),
            ],
            options={
                "db_table": "users",
            },
        ),
        migrations.CreateModel(
            name="TypeUserRole",
            fields=[
                (
                    "type_user_role_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=50)),
                ("level", models.IntegerField()),
                ("description", models.CharField(max_length=255)),
            ],
            options={
                "db_table": "type_user_role",
            },
        ),
        migrations.CreateModel(
            name="UserPreferences",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "value_display_mode",
                    models.CharField(
                        choices=[
                            ("itms", "ITMS/OTMS%"),
                            ("itmf", "ITMF/OTMF%"),
                            ("numeric", "Numeric"),
                        ],
                        default="itms",
                    ),
                ),
                (
                    "simulation_toolbar_strategy_added",
                    models.BooleanField(default=False),
                ),
                ("simulation_toolbar_margin_added", models.BooleanField(default=False)),
                (
                    "simulation_toolbar_hedge_irr_added",
                    models.BooleanField(default=False),
                ),
            ],
            options={
                "db_table": "user_preferences",
            },
        ),
        migrations.CreateModel(
            name="SSO",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("linkedin_id", models.CharField(max_length=255)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sso",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OTP",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("code", models.IntegerField()),
                (
                    "expired_at",
                    models.DateTimeField(
                        default=authentication.models.otp._expiry_time
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="otp",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "otp",
            },
        ),
        migrations.AddField(
            model_name="user",
            name="preferences",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user",
                to="authentication.userpreferences",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="type_user_role",
            field=models.ForeignKey(
                default="b73d082d-f0f7-4d63-a44b-688f726dd26b",
                on_delete=django.db.models.deletion.CASCADE,
                to="authentication.typeuserrole",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.BrinIndex(
                fields=["date_added"], name="user_index_date_added"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.BrinIndex(
                fields=["date_updated"], name="user_index_date_updated"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.HashIndex(
                fields=["is_deleted"], name="user_index_is_deleted"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.HashIndex(
                fields=["is_active"], name="user_index_is_active"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["email"], name="user_index_email"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.HashIndex(
                fields=["type_user_role_id"], name="user_index_type_user_role_id"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.BrinIndex(
                fields=["last_login"], name="user_index_date_last_login"
            ),
        ),
    ]