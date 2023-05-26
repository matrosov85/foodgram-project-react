from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from recipes.models import (
    Tag, Ingredient, Recipe, IngredientInRecipe, FavoriteRecipes, ShoppingCart
)
from users.models import User, Subscribe
from .filters import RecipeFilter, IngredientFilter
from .mixins import CreateDeleteMixin
from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    SubscriptionSerializer, TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipeMinifiedSerializer
)


class UsersViewset(UserViewSet, CreateDeleteMixin):
    pagination_class = Pagination
    lookup_field = 'pk'

    @action(detail=False)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribed__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(['POST', 'DELETE'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        return self.create_delete(
            serializer=SubscriptionSerializer, model=Subscribe, field='author'
        )


class TagViewset(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewset(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewset(ModelViewSet, CreateDeleteMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(['POST', 'DELETE'], detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        return self.create_delete(
            serializer=RecipeMinifiedSerializer, model=FavoriteRecipes, field='recipe'
        )

    @action(['POST', 'DELETE'], detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        return self.create_delete(
            serializer=RecipeMinifiedSerializer, model=ShoppingCart, field='recipe'
        )

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values('ingredient')
            .annotate(amount=Sum('amount'))
            .values_list('ingredient__name', 'ingredient__measurement_unit', 'amount')
        )
        data = [('{} ({}) - {}'.format(*ingredient)) for ingredient in ingredients]
        return HttpResponse('\n'.join(data), content_type='text/plain')
