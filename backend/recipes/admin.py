from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Tag, Ingredient, Recipe, IngredientInRecipe, FavoriteRecipes, ShoppingCart
)


class TagResource(resources.ModelResource):

    class Meta:
        model = Tag


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_classes = [TagResource]
    list_display = ('name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)

    class Meta:
        verbose_name = 'Тэги'


class IngredientResource(resources.ModelResource):

    class Meta:
        model = Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_classes = [IngredientResource]
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)

    class Meta:
        verbose_name = 'Ингредиенты'


class RecipeIngredientAdmin(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date', 'recipe_in_favorites')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    fields = ('author', 'name', 'tags', 'cooking_time', 'text', 'image')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientAdmin,)

    @admin.display(description='Добавлен в избранное')
    def recipe_in_favorites(self, recipe):
        return recipe.favorite.count()

    class Meta:
        verbose_name = 'Рецепты'


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

    class Meta:
        verbose_name = 'Избранное'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

    class Meta:
        verbose_name = 'Список покупок'
