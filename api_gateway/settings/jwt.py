from datetime import timedelta
from .config import ACCESS_TTL, REFRESH_TTL

from api_gateway.settings.config import ACCESS_TTL, REFRESH_TTL

SIMPLE_JWT = {
    "USER_ID_FIELD": "user_id",
    "ACCESS_TOKEN_LIFETIME": timedelta(days=ACCESS_TTL),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=REFRESH_TTL),
}
