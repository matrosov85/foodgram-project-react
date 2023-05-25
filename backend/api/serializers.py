from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer, UserCreateSerializer

from recipes.models import Tag, Ingredient, Recipe, IngredientInRecipe
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
    
    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscriber.filter(author=author).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, author):
        queryset = author.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = RecipeMinifiedSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, author):
        return author.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, ingredients_in_recipe):
        return ingredients_in_recipe.ingredient.name

    def get_measurement_unit(self, ingredients_in_recipe):
        return ingredients_in_recipe.ingredient.measurement_unit

    def to_representation(self, ingredients_in_recipe):
        representation = super().to_representation(ingredients_in_recipe)
        representation['id'] = ingredients_in_recipe.ingredient.id
        return representation
    
    def to_internal_value(self, ingredients_in_recipe):
        internal_value = super().to_internal_value(ingredients_in_recipe)
        internal_value['id'] = ingredients_in_recipe['id']
        return internal_value


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_in_recipe', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorite.filter(recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=recipe).exists()
        return False


class RecipeSerializer(RecipeReadSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('Обязтельное поле')
        if len(tags) != len(set(tags)):
            raise ValidationError('Теги не должны повторяться')
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError('Обязтельное поле')
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError('Ингридиенты не должны повторяться')
            if int(item['amount']) < 1:
                raise ValidationError('Убедитесь, что это значение больше либо равно 1')
            ingredients_list.append(ingredient)
        return ingredients

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            ingredient = Ingredient.objects.get(**ingredient)
            IngredientInRecipe.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(recipe, validated_data)
        recipe.ingredients.clear()
        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            ingredient = Ingredient.objects.get(**ingredient)
            IngredientInRecipe.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
