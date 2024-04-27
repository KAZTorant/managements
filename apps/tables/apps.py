from django.apps import AppConfig


class TablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tables'

    def ready(self) -> None:
        import apps.tables.signals
        return super().ready()