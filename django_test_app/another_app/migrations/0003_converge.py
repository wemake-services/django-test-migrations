from django.db import migrations, models


class Migration(migrations.Migration):
    """Depends on multiple apps."""

    dependencies = [
        ('another_app', '0002_add_field'),
        ('main_app', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            'dummymodel', 'converged', models.IntegerField(default=0)
        ),
    ]
