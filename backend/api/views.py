from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from recipes.models import (
    Tag, Ingredient, Recipe, IngredientInRecipe, FavoriteRecipes, ShoppingCart)
from users.models import User, Subscribe
from .filters import RecipeFilter, IngredientFilter
from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    SubscriptionSerializer, TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipeMinifiedSerializer
)


class UsersViewset(UserViewSet):
    pagination_class = Pagination

    @action(detail=False)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribed__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(['POST', 'DELETE'], detail=True, pagination_class=Pagination)
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = user.subscriber.filter(author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response({'errors': 'Подписка уже оформлена'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'errors': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Подписки не существует'},
                            status=status.HTTP_400_BAD_REQUEST)


class TagViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    # filter_backends = (SearchFilter,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    # search_fields = ('^name',)
    pagination_class = None


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(['POST', 'DELETE'], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = user.favorite.filter(recipe=recipe)

        if request.method == 'POST':
            if favorite.exists():
                return Response({'errors': 'Рецепт уже есть в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeMinifiedSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            FavoriteRecipes.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепта нет в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(['POST', 'DELETE'], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = user.shopping_cart.filter(recipe=recipe)
        if request.method == 'POST':
            if shopping_cart.exists():
                return Response({'errors': 'Рецепт уже есть в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeMinifiedSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if shopping_cart.exists():
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепта нет в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values('ingredient')
            .annotate(amount=Sum('amount'))
            .values_list('ingredient__name', 'ingredient__measurement_unit', 'amount')
        )
        data = []
        [data.append('{} ({}) - {}'.format(*ingredient)) for ingredient in ingredients]
        return HttpResponse('\n'.join(data), content_type='text/plain')
