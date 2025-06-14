from django.contrib import admin
from .models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingList,
)


@admin.register(Ingredient)
class IngredientPanel(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


class InlineRecipeIngredient(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipePanel(admin.ModelAdmin):
    list_display = ("name", "author", "cooking_time", "pub_date")
    search_fields = ("name", "author__email", "author__username")
    list_filter = ("author",)
    inlines = [InlineRecipeIngredient]


@admin.register(RecipeIngredient)
class RecipeIngredientPanel(admin.ModelAdmin):
    list_display = ("recipe", "component", "amount")
    search_fields = ("recipe__name", "component__name")


@admin.register(Favorite)
class FavoritePanel(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__email", "recipe__name")


@admin.register(ShoppingList)
class ShoppingListPanel(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__email", "recipe__name")
