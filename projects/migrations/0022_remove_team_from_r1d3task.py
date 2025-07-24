from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration to remove the team field from R1D3Task model.
    """

    dependencies = [
        ('projects', '0021_add_team_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='r1d3task',
            name='team',
        ),
    ]
