from django.db import migrations

from api_gateway.utils import populate_default_strategy


class Migration(migrations.Migration):
    dependencies = [
        ("strategy_simulation", "0016_merge_20240213_1352"),
    ]
    operations = [
        migrations.RunPython(populate_default_strategy),
    ]
