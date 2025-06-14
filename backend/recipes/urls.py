from django.urls import path
from .views import (
    IngredientListView,
    IngredientDetailView,
    RecipeListCreateView,
    RecipeDetailView,
    RecipeGetLinkView,
    ShoppingCartAddView,
    DownloadShoppingCartView,
    FavoriteAddView,
)

urlpatterns = [
    path("ingredients/", IngredientListView.as_view(), name="ingredient-list"),
    path("ingredients/<int:pk>/", IngredientDetailView.as_view(), name="ingredient-detail"),
    path("recipes/", RecipeListCreateView.as_view(), name="recipe-list-create"),
    path("recipes/<int:pk>/", RecipeDetailView.as_view(), name="recipe-detail"),
    path("recipes/<int:id>/get-link/", RecipeGetLinkView.as_view(), name="recipe-get-link"),
    path("recipes/<int:pk>/shopping_cart/", ShoppingCartAddView.as_view(), name="shopping-cart-add"),
    path("recipes/download_shopping_cart/", DownloadShoppingCartView.as_view(), name="download-shopping-cart"),
    path("recipes/<int:pk>/favorite/", FavoriteAddView.as_view(), name="favorite-add"),
]
