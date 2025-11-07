# Generated manually for text-based ownership
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_remove_arcadetask_team_remove_educationtask_team_and_more'),
    ]

    operations = [
        # Add text fields to BaseTask subclasses
        migrations.AddField(
            model_name='gamedevelopmenttask',
            name='created_by_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='gamedevelopmenttask',
            name='assigned_to_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='educationtask',
            name='created_by_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='educationtask',
            name='assigned_to_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='socialmediatask',
            name='created_by_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='socialmediatask',
            name='assigned_to_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='arcadetask',
            name='created_by_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='arcadetask',
            name='assigned_to_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='themeparktask',
            name='created_by_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='themeparktask',
            name='assigned_to_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='r1d3task',
            name='created_by_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='r1d3task',
            name='assigned_to_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        # Add to GameTask model as well
        migrations.AddField(
            model_name='gametask',
            name='created_by_name',
            field=models.CharField(blank=True, default='', help_text='Creator name for Git sync workflow', max_length=100),
        ),
        migrations.AddField(
            model_name='gametask',
            name='assigned_to_name',
            field=models.CharField(blank=True, default='', help_text='Team member name for Git sync workflow', max_length=100),
        ),
    ]
