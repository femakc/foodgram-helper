from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from foodgram.common import R_CHOICES
from recipes.models import (Favorite, IngredientProperty, Ingredients, Recipe,
                            Tags, TagsProperty, UserShopCart)
from rest_framework import serializers
from user.models import Follow, User


class TagsSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели Tags."""
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tags
        fields = [
            'id',
            'name',
            'color',
            'slug'
        ]

    def get_name(self, obj):
        return R_CHOICES[obj.name]


class IngredientPropertySerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели IngredientProperty."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientProperty
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class IngredientsSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели Ingredient."""

    class Meta:
        model = Ingredients
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class UserSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели User."""
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data['password']
        validated_data['password'] = make_password(password)
        return super().create(validated_data)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            # 'is_subscribed',
            'password',
        ]


class RecipeSerialzer(serializers.ModelSerializer):

    tags = TagsSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_ingredients(self, obj):
        ingredients = IngredientProperty.objects.filter(recipe=obj)
        return IngredientPropertySerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return UserShopCart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientProperty
        fields = ('id', 'amount',)


@transaction.atomic
class CreateRecipeSerialzer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    ingredients = AmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True,
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(
            limit_value=1,
            message='Время приготовления не может занимать меньше минуты'
        ),)
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            amount = ingredient['amount']
            if int(amount) < 1:
                raise serializers.ValidationError(
                    {'amount': 'Количество ингредиента не может быть равным 0'}
                )
        data['ingredients'] = ingredients
        return data

    @transaction.atomic
    def create_ingredients(self, ingredients, recipe):
        bulk_ingredient_list = [
            IngredientProperty(
                recipe=recipe,
                ingredient=Ingredients.objects.get(pk=ingredient_data['id']),
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients
        ]
        IngredientProperty.objects.bulk_create(bulk_ingredient_list)

    @transaction.atomic
    def create_tags(self, tags, recipe):
        bulk_tags_list = [
            TagsProperty(recipe=recipe, tags=Tags.objects.get(name=tag_data))
            for tag_data in tags
        ]
        TagsProperty.objects.bulk_create(bulk_tags_list)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user
        recipe = super().create(validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance = super().update(instance, validated_data)
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeSerialzer(instance, context={
            'request': self.context.get('request')
        }).data


class ShopingCardSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Recipe Shop Cart. """
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


@transaction.atomic
class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'token',
            'is_subscribed'
        ]

    def validate(self, data):
        if data['username'].lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть me'
            )
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                'email не соответствует User'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SetPasswordSerializer(serializers.ModelSerializer):
    """ Сериализатор эндпойнта SetPassword. """
    new_password = serializers.CharField(
        required=True,
        max_length=128,
        min_length=8,
        write_only=True
    )
    current_password = serializers.CharField(
        required=True,
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['new_password', 'current_password']

    def validate(self, attrs):
        if attrs['new_password'] == attrs['current_password']:
            raise serializers.ValidationError(
                'новый и старый пароли идентичны'
            )
        return super().validate(attrs)


@transaction.atomic
class UserSubscribtionsSerializer(serializers.ModelSerializer):
    """ Сериализатор эндпойнта UserSubscribtions. """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author_id=obj.id)
        serializer = ShopingCardSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author_id=obj.id)
        return recipes.count()

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context.get('user'),
            author=obj
        ).exists()

    @transaction.atomic
    def update(self, instance, validated_data):
        author = User.objects.get(username=self.context.get('author'))
        instance.email = author.email
        return instance


class FollowSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Follow. """

    result = UserSubscribtionsSerializer()

    class Meta:
        model = Follow
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Ingredient. """

    class Meta:
        model = Ingredients
        fields = '__all__'


class UsersSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Users List и Create. """

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]
