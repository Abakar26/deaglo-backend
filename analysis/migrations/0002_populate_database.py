from django.db import migrations

from api_gateway.utils import populate_analysis_role, populate_category


class Migration(migrations.Migration):
    dependencies = [
        ("analysis", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(populate_analysis_role),
        migrations.RunPython(populate_category),
    ]
