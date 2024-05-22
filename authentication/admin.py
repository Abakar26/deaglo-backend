from django.contrib import admin
from django.contrib.auth import get_user_model

from authentication.models import OTP, TypeUserRole

admin.site.register([get_user_model(), OTP, TypeUserRole])
