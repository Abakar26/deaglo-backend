from django.db import migrations

from api_gateway.utils import populate_default_strategy_leg


class Migration(migrations.Migration):
    dependencies = [
        ("strategy_simulation", "0012_strategysimulation_result_id"),
    ]
    operations = [
        migrations.RunPython(populate_default_strategy_leg),
    ]
