from django.db import migrations

from api_gateway.utils.populate_database import populate_user_role


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(populate_user_role),
    ]
