from django.db import migrations

from api_gateway.utils import populate_default_strategy, populate_default_strategy_leg


class Migration(migrations.Migration):
    dependencies = [
        (
            "strategy_simulation",
            "0007_strategy_remove_strategyinstance_custom_strategy_leg_and_more",
        ),
    ]
    operations = [
        migrations.RunPython(populate_default_strategy),
    ]
