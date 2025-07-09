# Generated manually to fix missing table in production

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0002_remove_is_completed_add_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='StrategyMilestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('target_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('phase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='strategy.strategyphase')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
