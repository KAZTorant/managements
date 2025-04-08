from django.apps import AppConfig


class PrintersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.printers'
    verbose_name = "Printer"

    def ready(self) -> None:
        return super().ready()
