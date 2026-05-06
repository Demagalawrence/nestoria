#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('find_your_perfect_home')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'find_your_perfect_home.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

def create_admin_user():
    User = get_user_model()
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
        print(f"✅ Admin user created successfully")
        admin_user.set_password('admin123')
        print(f"✅ Admin password set to: admin123")
    else:
        print(f"⚠️ Admin user already exists")
    
    if 'admin123' in admin_user.password:
        print(f"✅ Admin password already set correctly")
    else:
        admin_user.set_password('admin123')
        print(f"✅ Admin password updated to: admin123")

if __name__ == '__main__':
    create_admin_user()
