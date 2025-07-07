from django.db import migrations, models

def set_initial_status(apps, schema_editor):
    """
    Set the initial status values based on is_completed field
    """
    GameMilestone = apps.get_model('projects', 'GameMilestone')
    for milestone in GameMilestone.objects.all():
        if milestone.is_completed:
            milestone.status = 'completed'
        else:
            milestone.status = 'in_progress'
        milestone.save()

class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamemilestone',
            name='status',
            field=models.CharField(
                choices=[
                    ('not_started', 'Not Started'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed')
                ],
                default='not_started',
                max_length=20
            ),
        ),
        migrations.RunPython(set_initial_status),
    ]
