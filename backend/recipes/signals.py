import json
import logging
import os

from django.conf import settings
from django.core.files import File
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, RecipeIngredient

logger = logging.getLogger(__name__)
User = get_user_model()


def load_json_data(filename):
    filepath = os.path.join(settings.BASE_DIR, "data", filename)
    if not os.path.isfile(filepath):
        logger.error(f"Файл {filename} не найден по пути {filepath}")
        return []
    with open(filepath, encoding="utf-8") as json_file:
        return json.load(json_file)


def add_ingredients(ingredients_list):
    existing = {
        (ingredient.name.lower(), ingredient.measurement_unit.lower())
        for ingredient in Ingredient.objects.all()
    }
    to_create = []
    for item in ingredients_list:
        key = (item["name"].lower(), item["measurement_unit"].lower())
        if key not in existing:
            to_create.append(
                Ingredient(name=item["name"], measurement_unit=item["measurement_unit"])
            )
    Ingredient.objects.bulk_create(to_create)
    logger.info(f"Добавлено ингредиентов: {len(to_create)}")


def add_recipes(recipes_list):
    emails = {recipe["author_email"] for recipe in recipes_list}
    users = {user.email: user for user in User.objects.filter(email__in=emails)}

    ingredients_all = Ingredient.objects.all()
    ingredient_map = {
        (ing.name.lower(), ing.measurement_unit.lower()): ing for ing in ingredients_all
    }

    for recipe_data in recipes_list:
        author = users.get(recipe_data["author_email"])
        if not author:
            logger.error(f"Автор с email {recipe_data['author_email']} не найден, рецепт пропущен")
            continue

        recipe_obj, created = Recipe.objects.get_or_create(
            author=author,
            name=recipe_data["name"],
            defaults={
                "text": recipe_data["text"],
                "cooking_time": recipe_data["cooking_time"],
            },
        )

        if created:
            img_path = os.path.join(settings.MEDIA_ROOT, recipe_data["image"])
            if os.path.exists(img_path):
                with open(img_path, "rb") as img_file:
                    recipe_obj.image.save(os.path.basename(img_path), File(img_file), save=False)
            recipe_obj.save()
            logger.info(f"Добавлен рецепт: {recipe_obj.name}")

            links = []
            for ing in recipe_data["ingredients"]:
                key = (ing["name"].lower(), ing["measurement_unit"].lower())
                ingredient = ingredient_map.get(key)
                if not ingredient:
                    logger.warning(f"Ингредиент {key} не найден для рецепта {recipe_obj.name}")
                    continue
                links.append(
                    RecipeIngredient(recipe=recipe_obj, component=ingredient, amount=ing["amount"])
                )
            RecipeIngredient.objects.bulk_create(links)
        else:
            logger.info(f"Рецепт {recipe_obj.name} уже существует")


@receiver(post_migrate)
def load_sample_data(sender, **kwargs):
    ingredients = load_json_data("ingredients.json")
    if ingredients:
        add_ingredients(ingredients)

    recipes = load_json_data("recipes.json")
    if recipes:
        add_recipes(recipes)
