from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from http import HTTPStatus
from django.db.models import Sum, F

from recipes.models import Ingredient, Recipe, ShoppingList, RecipeIngredient, Favorite
from recipes.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    RecipeCartSerializer,
    RecipeShortSerializer,
)
from recipes.permissions import IsAuthorOrReadOnly


class IngredientListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]
    pagination_class = None


class IngredientDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecipeCreateSerializer
        return RecipeListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        output_serializer = RecipeListSerializer(recipe, context={"request": request})
        return Response(output_serializer.data, status=HTTPStatus.CREATED)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        params = self.request.query_params

        if user.is_authenticated:
            is_fav = params.get("is_favorited")
            if is_fav in ["1", "true", "True"]:
                queryset = queryset.filter(favorites__user=user)

            in_cart = params.get("is_in_shopping_cart")
            if in_cart in ["1", "true", "True"]:
                queryset = queryset.filter(in_carts__user=user)

        if "author" in params:
            queryset = queryset.filter(author__id=params["author"])

        return queryset


class RecipeGetLinkView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        full_url = request.build_absolute_uri(f"/api/recipes/{recipe.id}/")
        return Response({"short-link": full_url}, status=HTTPStatus.OK)


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthorOrReadOnly]
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return RecipeCreateSerializer
        return RecipeListSerializer

    def patch(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        read_serializer = RecipeListSerializer(instance, context={"request": request})
        return Response(read_serializer.data, status=HTTPStatus.OK)


class ShoppingCartAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if user.shopping_cart.filter(recipe=recipe).exists():
            return Response(
                {"detail": "Рецепт уже в корзине."}, status=HTTPStatus.BAD_REQUEST
            )
        user.shopping_cart.create(recipe=recipe)
        serializer = RecipeCartSerializer(recipe, context={"request": request})
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        cart_item = user.shopping_cart.filter(recipe=recipe).first()

        if not cart_item:
            return Response(
                {"detail": "Рецепт не найден в корзине."},
                status=HTTPStatus.BAD_REQUEST,
            )
        cart_item.delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class DownloadShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        shopping_items = user.shopping_cart.all()

        if not shopping_items.exists():
            return Response({"detail": "Корзина пуста."}, status=HTTPStatus.BAD_REQUEST)

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in=shopping_items.values_list("recipe", flat=True)
            )
            .values(name=F("component__name"), unit=F("component__measurement_unit"))
            .annotate(amount=Sum("amount"))
            .order_by("name")
        )

        lines = [f"{item['name']} — {item['amount']} {item['unit']}" for item in ingredients]
        content = "\n".join(lines)
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="shopping_cart.txt"'
        return response


class FavoriteAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if user.favorites.filter(recipe=recipe).exists():
            return Response(
                {"detail": "Рецепт уже в избранном."}, status=HTTPStatus.BAD_REQUEST
            )
        user.favorites.create(recipe=recipe)
        serializer = RecipeShortSerializer(recipe, context={"request": request})
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = user.favorites.filter(recipe=recipe).first()

        if not favorite:
            return Response(
                {"detail": "Рецепт не найден в избранном."}, status=HTTPStatus.BAD_REQUEST
            )
        favorite.delete()
        return Response(status=HTTPStatus.NO_CONTENT)
