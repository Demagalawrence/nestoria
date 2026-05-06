from django.core.management.base import BaseCommand, Command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user in production'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            help='Set password for admin user'
        )

    def handle(self, *args, **options):
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            email='admin@renthu.ug',
            first_name='Admin',
            last_name='User',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'role': 'admin'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
        
        # Set password if provided
        password = options.get('password')
        if password:
            admin_user.set_password(password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin password set to: {password}'))
        else:
            self.stdout.write(self.style.WARNING('Use --password to set admin password'))
