# Generated by Django 5.2.3 on 2025-07-03 15:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('timeframe', models.CharField(choices=[('short', 'Short-term (< 1 year)'), ('medium', 'Medium-term (1-3 years)'), ('long', 'Long-term (3+ years)')], max_length=10)),
                ('target_date', models.DateField()),
                ('is_completed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StrategyPhase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('phase_type', models.CharField(choices=[('indie_dev', 'Indie Game Development'), ('arcade', 'Arcade Machines'), ('theme_park', 'Theme Park Attractions')], max_length=20)),
                ('description', models.TextField()),
                ('order', models.PositiveIntegerField(help_text='Order in the roadmap sequence')),
                ('start_year', models.IntegerField(help_text='Estimated start year')),
                ('end_year', models.IntegerField(help_text='Estimated completion year')),
                ('is_current', models.BooleanField(default=False, help_text='Is this the current active phase?')),
                ('is_completed', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Vision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('target_year', models.IntegerField(help_text='Target year for achieving this vision')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Objective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('due_date', models.DateField()),
                ('is_completed', models.BooleanField(default=False)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='objectives', to='strategy.goal')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_objectives', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KeyResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('target_value', models.FloatField(help_text='Target numerical value to achieve')),
                ('current_value', models.FloatField(default=0, help_text='Current progress towards target')),
                ('unit', models.CharField(help_text='Unit of measurement (%, $, etc.)', max_length=50)),
                ('objective', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='key_results', to='strategy.objective')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StrategyMilestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('target_date', models.DateField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('phase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='strategy.strategyphase')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='goal',
            name='vision',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='strategy.vision'),
        ),
    ]
