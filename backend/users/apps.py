from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # Импортируем сигналы при готовности приложения
        import users.signals  # noqa: F401

