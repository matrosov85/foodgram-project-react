from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersViewset, TagViewset, RecipeViewset, IngredientViewset


router = DefaultRouter()
router.register('users', UsersViewset, basename='users')
router.register('tags', TagViewset, basename='tags')
router.register('recipes', RecipeViewset, basename='recipes')
router.register('ingredients', IngredientViewset, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
