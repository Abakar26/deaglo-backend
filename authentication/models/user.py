import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    UnicodeUsernameValidator,
)
from django.contrib.postgres.indexes import BrinIndex, HashIndex
from django.db import models, transaction


class UserProfileManager(BaseUserManager):
    """User manager for User Model"""

    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserPreferences(models.Model):
    """
    Model for storing user preferences
    """

    class Meta:
        db_table = "user_preferences"

    VALUE_DISPLAY_MODE_CHOICES = (
        ("itms", "ITMS/OTMS%"),
        ("itmf", "ITMF/OTMF%"),
        ("numeric", "Numeric"),
    )
    value_display_mode = models.CharField(
        choices=VALUE_DISPLAY_MODE_CHOICES, default="itms"
    )

    simulation_toolbar_strategy_added = models.BooleanField(default=False)
    simulation_toolbar_margin_added = models.BooleanField(default=False)
    simulation_toolbar_hedge_irr_added = models.BooleanField(default=False)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for managing user information and authentication.
    """

    class Meta:
        db_table = "users"
        indexes = [
            BrinIndex(fields=["date_added"], name="user_index_date_added"),
            BrinIndex(fields=["date_updated"], name="user_index_date_updated"),
            HashIndex(fields=["is_deleted"], name="user_index_is_deleted"),
            HashIndex(fields=["is_active"], name="user_index_is_active"),
            models.Index(fields=["email"], name="user_index_email"),
            HashIndex(
                fields=["type_user_role_id"], name="user_index_type_user_role_id"
            ),
            BrinIndex(fields=["last_login"], name="user_index_date_last_login"),
        ]

    COMPANY_TYPE_CHOICES = (
        ("BF", "Banks and Financial Institutions"),
        ("MNC", "Multinational Corporations"),
        ("IE", "Import/Export Businesses"),
        ("HEDGE", "Hedge Funds"),
        ("ALT", "Alternative Asset Managers (Private Equity, Credit, etc.)"),
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
    )

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, validators=[UnicodeUsernameValidator])
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=12)
    country = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    company_type = models.CharField(choices=COMPANY_TYPE_CHOICES)

    preferences = models.OneToOneField(
        UserPreferences, on_delete=models.CASCADE, related_name="user"
    )

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    type_user_role = models.ForeignKey(
        "authentication.TypeUserRole",
        on_delete=models.CASCADE,
        default="b73d082d-f0f7-4d63-a44b-688f726dd26b",
    )
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="user",
    )

    objects = UserProfileManager()
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not hasattr(self, "preferences"):
            with transaction.atomic():
                UserPreferences.objects.create(user=self)
        super().save(*args, **kwargs)

    def delete(self, **kwargs):
        self.is_deleted = True
        self.save()

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_staff(self):
        return (
            str(self.type_user_role.type_user_role_id)
            == "c2c7c40c-56e1-4576-9309-7ca3fb7cac89"
        )

    @property
    def is_superuser(self):
        return self.is_staff

    @is_staff.setter
    def is_staff(self, value):
        if value:
            self.type_user_role_id = "c2c7c40c-56e1-4576-9309-7ca3fb7cac89"
        else:
            self.type_user_role_id = "b73d082d-f0f7-4d63-a44b-688f726dd26b"
        self.save()

    @is_superuser.setter
    def is_superuser(self, value):
        self.is_staff = value
