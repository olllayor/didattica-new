from django.apps import AppConfig

class AIChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aichat'

    def ready(self):
        """Import signals when app is ready"""
        import aichat.models