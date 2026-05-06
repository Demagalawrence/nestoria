#!/usr/bin/env python
import os
import sys
import django

# Add project directory to Python path
sys.path.append('find_your_perfect_home')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'find_your_perfect_home.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

def update_admin_password():
    User = get_user_model()
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.set_password('admin123')
        print(f"✅ Admin password updated to: admin123")
        print(f"✅ You can now login with:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   URL: https://nestoria-tan.vercel.app/admin")
        
    except User.DoesNotExist:
        print(f"❌ Admin user not found in database")
    except Exception as e:
        print(f"❌ Error updating admin password: {str(e)}")

if __name__ == '__main__':
    update_admin_password()
