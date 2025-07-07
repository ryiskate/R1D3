from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(default='fa-book', help_text='FontAwesome icon class', max_length=50)),
                ('color', models.CharField(default='#4e73df', help_text='Hex color code', max_length=20)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Knowledge Category',
                'verbose_name_plural': 'Knowledge Categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='KnowledgeTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Knowledge Tag',
                'verbose_name_plural': 'Knowledge Tags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='KnowledgeArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('summary', models.TextField(help_text='Brief summary of the article')),
                ('content', models.TextField(help_text='Main content in HTML format')),
                ('featured_image', models.ImageField(blank=True, help_text='Featured image for the article', null=True, upload_to='knowledge/images/')),
                ('is_published', models.BooleanField(default=True)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='education.knowledgecategory')),
                ('tags', models.ManyToManyField(blank=True, related_name='articles', to='education.knowledgetag')),
            ],
            options={
                'verbose_name': 'Knowledge Article',
                'verbose_name_plural': 'Knowledge Articles',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='MediaAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='knowledge/attachments/')),
                ('file_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video'), ('document', 'Document'), ('audio', 'Audio'), ('other', 'Other')], default='image', max_length=50)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='education.knowledgearticle')),
            ],
            options={
                'verbose_name': 'Media Attachment',
                'verbose_name_plural': 'Media Attachments',
                'ordering': ['created_at'],
            },
        ),
    ]
