from django.db import migrations, models


class Migration(migrations.Migration):
    """Add a test field to the model"""

    dependencies = [('another_app', '0001_initial')]

    operations = [
        migrations.AddField(
            'dummymodel', 'test_field', models.IntegerField(default=0)
        ),
    ]
