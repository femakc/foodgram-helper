from base64 import b64decode

import webcolors
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram.settings import R_CHOICES
from recipes.models import (
    Ingredient,
    IngredientProperty,
    Recipe,
    Tags,
    TagsProperty
)
from user.models import Follow, User


class Hex2NameColor(serializers.Field):
    """ Преобразование HEX цвета """
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagsSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели Tags."""
    color = Hex2NameColor()
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

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
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
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit',
            # 'amount'
        ]


class UserSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели User."""
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

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
            'is_subscribed',
            'password',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email'),
                message='Имя пользователя или email уже используются'
            )
        ]


class RecipeSerialzer(serializers.ModelSerializer):
    """ Сериализатор модели Recipe. """

    tags = TagsSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

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

    def to_internal_value(self, data) -> dict:
        decode_data = data.get('image')
        image_data = b64decode(decode_data.split(',')[1])
        image = ContentFile(image_data, 'backend-static/image.jpg')
        cooking_time = data.get('cooking_time')
        is_favorited = data.get('is_favorited')
        is_in_shopping_cart = data.get('is_in_shopping_cart')
        name = data.get('name')
        text = data.get('text')
        ingredients = data.get('ingredients')
        tags = data.get('tags')

        def ingregient_validator(dicts) -> bool:
            key_list = []
            for i in dicts:
                if not Ingredient.objects.filter(pk=i['id']).exists():
                    return True
                if i['id'] in key_list:
                    return True
                key_list.append(i['id'])
            return False

        def tags_validator(tags) -> bool:
            tags_list = []
            for i in tags:
                if not Tags.objects.filter(pk=i).exists():
                    return True
                if i in tags_list:
                    return True
                tags_list.append(i)
            return False

        if not name:
            raise serializers.ValidationError({
                'name': 'Это обязательное поле.'
            })
        if not text:
            raise serializers.ValidationError({
                'text': 'Это обязательное поле'
            })
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Это обязательное поле'
            })
        if ingregient_validator(ingredients):
            raise serializers.ValidationError({
                'ingredients': 'Не валидный ингредиент!'
            })
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Это обязательное поле'
            })
        if tags_validator(tags):
            raise serializers.ValidationError({
                'tags': 'Не валидный тег'
            })
        if not image:
            raise serializers.ValidationError({
                'image': 'Это обязательное поле.'
            })
        if not cooking_time:
            raise serializers.ValidationError({
                'cooking_time': 'Это обязательное поле.'
            })
        if not is_favorited:
            is_favorited = False
        if not is_in_shopping_cart:
            is_in_shopping_cart = False

        return {
            'name': name,
            'text': text,
            'ingredients': ingredients,
            'tags': tags,
            'image': image,
            'cooking_time': cooking_time,
            'is_favorited': is_favorited,
            'is_in_shopping_cart': is_in_shopping_cart
        }

    def create_ingredient(self, ingredients_data, recipe) -> None:
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(
                pk=ingredient_data['id']
            )
            IngredientProperty.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )

    def create_tags(self, tags_data, recipe) -> None:
        for tag_data in tags_data:
            TagsProperty.objects.update_or_create(
                recipe=recipe,
                tags=Tags.objects.get(pk=tag_data)
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredient(ingredients_data, recipe)
        self.create_tags(tags_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        TagsProperty.objects.filter(recipe_id=instance.id).delete()
        IngredientProperty.objects.filter(recipe_id=instance.id).delete()
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        self.create_ingredient(ingredients_data, instance)
        self.create_tags(tags_data, instance)
        instance.save()
        return instance


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
                "Имя пользователя не может быть 'me' "
            )
        user = User.objects.filter(email=data['email'])
        if user.exists():
            username = User.objects.filter(
                username=data['username'],
                email=data['email']
            )
        else:
            username = User.objects.filter(username=data['username'])
            if username.exists():
                raise serializers.ValidationError(
                    "email не соответствует User "
                )

        return data

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
                "новый и старый пароли идентичны"
            )
        return super().validate(attrs)


class UserSubscribtionsSerializer(serializers.ModelSerializer):
    """ Сериализатор эндпойнта UserSubscribtions. """

    recipes = ShopingCardSerializer(many=True)
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

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('user')
        author = Follow.objects.filter(user=user, author=obj).exists()
        return author

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        author = User.objects.get(username=self.context.get('author'))
        instance.email = author.email
        return instance


class FollowSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Follow. """

    result = UserSubscribtionsSerializer()

    class Meta:
        model = Follow
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Ingredient. """

    class Meta:
        model = Ingredient
        fields = "__all__"


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
