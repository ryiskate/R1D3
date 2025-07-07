# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategymilestone',
            name='status',
            field=models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='not_started', max_length=20),
        ),
        migrations.RunSQL(
            "UPDATE strategy_strategymilestone SET status = CASE WHEN is_completed THEN 'completed' ELSE 'not_started' END;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveField(
            model_name='strategymilestone',
            name='is_completed',
        ),
    ]
