from django.apps import AppConfig

class USSDConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ussd'
    verbose_name = 'USSD System'
    
    def ready(self):
        # Default menu will be created via migration
        pass
