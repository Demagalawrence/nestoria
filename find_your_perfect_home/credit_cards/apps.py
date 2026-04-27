from django.apps import AppConfig

class CreditCardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'credit_cards'
    verbose_name = 'Credit Cards'
    
    def ready(self):
        # Default providers will be created via migration
        pass
