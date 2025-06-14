from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from foodgram.constants import (
    MAX_COOKING_TIME,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_AMOUNT,
)

User = settings.AUTH_USER_MODEL


class Ingredient(models.Model):
    title = models.CharField("Название ингредиента", max_length=200)
    unit = models.CharField("Единица измерения", max_length=200)

    class Meta:
        ordering = ["title"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["title", "unit"],
                name="ingredient_unique_combination"
            )
        ]

    def __str__(self):
        return f"{self.title}, {self.unit}"


class Recipe(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_recipes",
        verbose_name="Автор рецепта"
    )
    title = models.CharField("Название рецепта", max_length=200)
    picture = models.ImageField("Изображение", upload_to="recipes/")
    description = models.TextField("Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты"
    )
    prep_time = models.PositiveSmallIntegerField(
        "Время приготовления (в минутах)",
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_list",
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент"
    )
    quantity = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="recipe_ingredient_unique"
            )
        ]

    def __str__(self):
        return f"{self.ingredient.title} – {self.quantity} ({self.recipe.title})"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="liked_recipes",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="liked_by",
        verbose_name="Рецепт"
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_fav_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.recipe}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="added_to_cart",
        verbose_name="Рецепт"
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_cart_entry"
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.recipe}"
