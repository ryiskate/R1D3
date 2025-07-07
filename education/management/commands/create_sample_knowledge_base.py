from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from education.knowledge_models import KnowledgeCategory, KnowledgeTag, KnowledgeArticle


class Command(BaseCommand):
    help = 'Creates sample Knowledge Base content for demonstration purposes'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@r1d3.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create categories
        categories = [
            {
                'name': 'Getting Started',
                'description': 'Basic information for new users',
                'icon': 'fa-rocket',
                'color': '#4e73df'
            },
            {
                'name': 'Game Development',
                'description': 'Resources for game developers',
                'icon': 'fa-gamepad',
                'color': '#1cc88a'
            },
            {
                'name': 'Education Resources',
                'description': 'Materials for educators and students',
                'icon': 'fa-graduation-cap',
                'color': '#f6c23e'
            },
            {
                'name': 'Technical Documentation',
                'description': 'Technical guides and API documentation',
                'icon': 'fa-code',
                'color': '#e74a3b'
            }
        ]
        
        created_categories = []
        for i, category_data in enumerate(categories):
            category, created = KnowledgeCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon'],
                    'color': category_data['color'],
                    'order': i
                }
            )
            created_categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Create tags
        tags = ['Beginner', 'Intermediate', 'Advanced', 'Tutorial', 'Reference', 'Guide']
        created_tags = []
        for tag_name in tags:
            tag, created = KnowledgeTag.objects.get_or_create(name=tag_name)
            created_tags.append(tag)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tag: {tag.name}'))
            else:
                self.stdout.write(f'Tag already exists: {tag.name}')
        
        # Create articles
        articles = [
            {
                'title': 'Welcome to R1D3 Knowledge Base',
                'summary': 'An introduction to the R1D3 Knowledge Base system',
                'content': """
                <h2>Welcome to the R1D3 Knowledge Base!</h2>
                <p>This Knowledge Base is designed to provide you with all the information you need to succeed in the R1D3 ecosystem.</p>
                <p>Here you'll find guides, tutorials, reference materials, and best practices for all aspects of R1D3.</p>
                <h3>How to Use the Knowledge Base</h3>
                <ul>
                    <li>Browse by category using the sidebar navigation</li>
                    <li>Search for specific topics using the search bar</li>
                    <li>Filter articles by tags to find exactly what you need</li>
                </ul>
                <p>If you have any questions or suggestions for new articles, please contact the Education Department.</p>
                """,
                'category': created_categories[0],
                'tags': [created_tags[0], created_tags[3]]
            },
            {
                'title': 'Game Development Fundamentals',
                'summary': 'Learn the basics of game development at R1D3',
                'content': """
                <h2>Game Development Fundamentals</h2>
                <p>This article covers the fundamental concepts and processes used in game development at R1D3.</p>
                <h3>The Game Development Process</h3>
                <ol>
                    <li><strong>Concept Development</strong>: Brainstorming and defining the core game concept</li>
                    <li><strong>Pre-production</strong>: Creating design documents, prototypes, and planning</li>
                    <li><strong>Production</strong>: Building the game, including programming, art, and sound</li>
                    <li><strong>Testing</strong>: Quality assurance and bug fixing</li>
                    <li><strong>Release</strong>: Launching the game to the public</li>
                    <li><strong>Post-release</strong>: Updates, patches, and additional content</li>
                </ol>
                <h3>Key Resources</h3>
                <p>Be sure to check out our Game Design Document templates and coding standards in the Technical Documentation section.</p>
                """,
                'category': created_categories[1],
                'tags': [created_tags[0], created_tags[3], created_tags[5]]
            },
            {
                'title': 'Course Creation Guide',
                'summary': 'How to create effective educational courses',
                'content': """
                <h2>Course Creation Guide</h2>
                <p>This guide will help you create engaging and effective educational courses for the R1D3 platform.</p>
                <h3>Course Structure</h3>
                <p>A well-structured course typically includes:</p>
                <ul>
                    <li>Clear learning objectives</li>
                    <li>Engaging content in multiple formats (text, video, interactive)</li>
                    <li>Practice exercises and assessments</li>
                    <li>Feedback mechanisms</li>
                    <li>Resources for further learning</li>
                </ul>
                <h3>Best Practices</h3>
                <p>When creating courses, remember to:</p>
                <ul>
                    <li>Focus on practical, applicable knowledge</li>
                    <li>Break content into digestible chunks</li>
                    <li>Include real-world examples</li>
                    <li>Design for different learning styles</li>
                    <li>Create opportunities for active learning</li>
                </ul>
                """,
                'category': created_categories[2],
                'tags': [created_tags[1], created_tags[5]]
            },
            {
                'title': 'R1D3 API Documentation',
                'summary': 'Technical documentation for the R1D3 API',
                'content': """
                <h2>R1D3 API Documentation</h2>
                <p>This technical documentation covers the R1D3 API endpoints, authentication, and usage examples.</p>
                <h3>Authentication</h3>
                <p>All API requests require authentication using JWT tokens. To obtain a token:</p>
                <pre><code>
                POST /api/auth/token/
                {
                    "username": "your_username",
                    "password": "your_password"
                }
                </code></pre>
                <h3>Common Endpoints</h3>
                <ul>
                    <li><code>GET /api/games/</code> - List all games</li>
                    <li><code>GET /api/games/{id}/</code> - Retrieve a specific game</li>
                    <li><code>POST /api/games/</code> - Create a new game</li>
                    <li><code>PUT /api/games/{id}/</code> - Update a game</li>
                    <li><code>DELETE /api/games/{id}/</code> - Delete a game</li>
                </ul>
                <h3>Response Format</h3>
                <p>All API responses are in JSON format and include a status code and data payload.</p>
                """,
                'category': created_categories[3],
                'tags': [created_tags[2], created_tags[4]]
            }
        ]
        
        for article_data in articles:
            article, created = KnowledgeArticle.objects.get_or_create(
                title=article_data['title'],
                defaults={
                    'summary': article_data['summary'],
                    'content': article_data['content'],
                    'category': article_data['category'],
                    'author': admin_user
                }
            )
            if created:
                for tag in article_data['tags']:
                    article.tags.add(tag)
                self.stdout.write(self.style.SUCCESS(f'Created article: {article.title}'))
            else:
                self.stdout.write(f'Article already exists: {article.title}')
        
        self.stdout.write(self.style.SUCCESS('Sample Knowledge Base content created successfully!'))
