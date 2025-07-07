from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_add_status_to_milestone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamemilestone',
            name='is_completed',
        ),
    ]
