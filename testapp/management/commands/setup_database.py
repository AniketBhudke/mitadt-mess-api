from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Setup database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up database...')
        
        # Run migrations
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=0)
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Creating superuser...')
            User.objects.create_superuser(
                username='admin',
                email='admin@mitadt.edu.in',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created: admin/admin123'))
        
        self.stdout.write(self.style.SUCCESS('Database setup complete!'))