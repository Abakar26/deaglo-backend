from django.db import migrations

from api_gateway.utils import (
    populate_currency,
    populate_status,
    populate_tool,
)


class Migration(migrations.Migration):
    dependencies = [
        ("api_gateway", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(populate_currency),
        migrations.RunPython(populate_status),
        migrations.RunPython(populate_tool),
    ]
