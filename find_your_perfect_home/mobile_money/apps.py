from django.apps import AppConfig

class MobileMoneyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobile_money'
    verbose_name = 'Mobile Money'
    
    def ready(self):
        # Default providers will be created via migration
        pass
