from django.apps import AppConfig


class RecipeModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recipes"

    def ready(self):
        # Импорт сигналов при инициализации приложения
        from recipes import signals  # noqa: F401
