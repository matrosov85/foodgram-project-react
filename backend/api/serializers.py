from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField
)
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from config.settings import LIMIT_QUERY_PARAM
from recipes.models import Tag, Ingredient, Recipe, IngredientInRecipe
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
    
    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return user.is_authenticated and user.subscriber.filter(author=author).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance
        if user.subscriber.filter(author=author).exists():
            raise ValidationError({'errors': 'Подписка уже оформлена'})
        if user == author:
            raise ValidationError({'errors': 'Нельзя подписаться на себя'})
        return data

    def get_recipes(self, author):
        queryset = author.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.query_params.get(LIMIT_QUERY_PARAM)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = RecipeMinifiedSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, author):
        return author.recipes.count()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(ModelSerializer):
    name = SerializerMethodField()
    measurement_unit = SerializerMethodField()

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


class RecipeMinifiedSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')

    def validate(self, data):
        action = self.context.get('action')
        user = self.context.get('request').user
        recipe = self.instance
        if (
            action == 'shopping_cart' and
            user.shopping_cart.filter(recipe=recipe).exists()
        ):
            raise ValidationError({'errors': 'Рецепт уже есть в корзине'})
        if (
            action == 'favorite' and
            user.favorite.filter(recipe=recipe).exists()
        ):
            raise ValidationError({'errors': 'Рецепт уже есть в избранном'})
        return data


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_in_recipe', many=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return user.is_authenticated and user.favorite.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return (user.is_authenticated and
                user.shopping_cart.filter(recipe=recipe).exists()
        )


class RecipeSerializer(RecipeReadSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=True)
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
            ingredient = item['id']
            if ingredient in ingredients_list:
                raise ValidationError('Ингридиенты не должны повторяться')
            if int(item['amount']) < 1:
                raise ValidationError('Убедитесь, что это значение больше либо равно 1')
            ingredients_list.append(ingredient)
        return ingredients

    def set_ingredients(self, recipe, ingredients):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                amount=ingredient.pop('amount'),
                ingredient=Ingredient.objects.get(**ingredient),
                recipe=recipe
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(recipe, validated_data)
        recipe.ingredients.clear()
        self.set_ingredients(recipe, ingredients)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
