from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "avatar",
    ]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
    ]
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Личная информация",
            {"fields": ("first_name", "last_name", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "author")
    search_fields = ("subscriber__email", "author__email")
