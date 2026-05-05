# Generated migration to fix payment model references

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_payment_booking'),
    ]

    operations = [
        # This is a no-op migration to ensure proper model references
        migrations.RunPython(
            migrations.RunPython.noop,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
