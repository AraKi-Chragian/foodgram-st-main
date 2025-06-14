from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        verbose_name="Email",
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        blank=False,
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "author"],
                name="unique_subscription"
            )
        ]

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
