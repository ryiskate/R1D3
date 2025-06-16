from django.core.management.base import BaseCommand
from django.urls import reverse, NoReverseMatch

class Command(BaseCommand):
    help = 'Debug URL resolution issues'

    def handle(self, *args, **options):
        try:
            # Try to resolve the URL with namespace
            url = reverse('games:game_detail', kwargs={'pk': 3})
            self.stdout.write(self.style.SUCCESS(f'Successfully resolved URL: {url}'))
        except NoReverseMatch as e:
            self.stdout.write(self.style.ERROR(f'Error resolving URL with namespace: {e}'))

        try:
            # Try to resolve the URL without namespace
            url = reverse('game_detail', kwargs={'pk': 3})
            self.stdout.write(self.style.SUCCESS(f'Successfully resolved URL without namespace: {url}'))
        except NoReverseMatch as e:
            self.stdout.write(self.style.ERROR(f'Error resolving URL without namespace: {e}'))

        # List all available URL patterns
        from django.urls import get_resolver
        resolver = get_resolver()
        self.stdout.write(self.style.SUCCESS('Available URL patterns:'))
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'name') and pattern.name:
                self.stdout.write(f'  - {pattern.name}')
            elif hasattr(pattern, 'app_name') and pattern.app_name:
                self.stdout.write(f'  - App: {pattern.app_name}')
                if hasattr(pattern, 'namespace') and pattern.namespace:
                    self.stdout.write(f'    Namespace: {pattern.namespace}')
