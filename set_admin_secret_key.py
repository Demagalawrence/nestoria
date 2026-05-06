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

def set_admin_secret_key():
    User = get_user_model()
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.secret_key = '1234'
        admin_user.save()
        print(f"✅ Admin secret key set to: 1234")
        print(f"✅ Admin user: {admin_user.username}")
        print(f"✅ You can now login with:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Secret Key: 1234")
    except User.DoesNotExist:
        print(f"❌ Admin user not found in database")
    except Exception as e:
        print(f"❌ Error setting secret key: {str(e)}")

if __name__ == '__main__':
    set_admin_secret_key()
