from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersViewset, TagViewset, RecipeViewset, IngredientViewset


router = DefaultRouter()
router.register(r'users', UsersViewset, basename='users')
router.register(r'tags', TagViewset, basename='tags')
router.register(r'recipes', RecipeViewset, basename='recipes')
router.register(r'ingredients', IngredientViewset, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
