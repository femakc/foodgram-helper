from rest_framework import serializers, exceptions, status
from .models import Tag, Recipe, Ingredient, IngredientProperty, TagProperty
import webcolors
from foodgram.settings import R_CHOICES
from user.serializers import UserSerializer
import base64
import io
from PIL import Image

from base64 import b64decode
from django.core.files.base import ContentFile


class Hex2NameColor(serializers.Field):
    """ Преобразование HEX цвета """
    # При чтении данных ничего не меняем - просто возвращаем как есть
    def to_representation(self, value):
        return value
    # При записи код цвета конвертируется в его название
    def to_internal_value(self, data):
        # Доверяй, но проверяй
        try:
            # Если имя цвета существует, то конвертируем код в название
            data = webcolors.hex_to_name(data)
        except ValueError:
            # Иначе возвращаем ошибку
            raise serializers.ValidationError('Для этого цвета нет имени')
        # Возвращаем данные в новом формате
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()
    name = serializers.SerializerMethodField()
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug'
        ]

    def get_name(self, obj):
        return R_CHOICES[obj.name]


class IngredientPropertySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientProperty
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class IngredientsSerializer(serializers.ModelSerializer):
    # amount = serializers.ModelField(model_field=IngredientProperty()._meta.get_field('amount'))
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit',
            # 'amount'
        ]        

class RecipeSerialzer(serializers.ModelSerializer):
    tag = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tag',
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
        image = ContentFile(image_data, 'image.jpg')
        # author = self.context.get('request').user
        cooking_time = data.get('cooking_time')
        is_favorited = data.get('is_favorited')
        is_in_shopping_cart = data.get('is_in_shopping_cart')
        # name = data.get('name')
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

        def tag_validator(tags) -> bool:
            tags_list = []
            for i in tags:
                if not Tag.objects.filter(pk=i).exists():
                    return True
                if i in tags_list:
                    return True
                tags_list.append(i)
            return False

        # if name:
        #     if Recipe.objects.filter(name=name).exists():
        #         raise serializers.ValidationError({
        #         'name': 'Рецепт с таким именем уже существует'
        #     })
        # else:
        #     raise serializers.ValidationError({
        #         'name': 'Это обязательное поле.'
        #     })
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
        if tag_validator(tags):
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
            # 'name': name,
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
            IngredientProperty.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )

    def create_tag(self, tags_data, recipe) -> None:
        for tag_data in tags_data:
            TagProperty.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(pk=tag_data)
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data =validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredient(ingredients_data, recipe)
        self.create_tag(tags_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        # Recipe.objects.filter(pk=instance.id).delete()
        TagProperty.objects.filter(recipe_id=instance.id).delete()
        IngredientProperty.objects.filter(recipe_id=instance.id).delete()
        ingredients_data = validated_data.pop('ingredients')
        tags_data =validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.update_or_create(author=author, **validated_data)
        self.create_ingredient(ingredients_data, instance)
        self.create_tag(tags_data, instance)
        return recipe
