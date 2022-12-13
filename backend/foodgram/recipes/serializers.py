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


class IngredientAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientProperty
        fields = ['amount']


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
    author = UserSerializer()
    ingredients = IngredientsSerializer(many=True)

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

    # def decodeImage(self, obj):
    #     try:
    #         s = base64.b64decode(s.encode('UTF-8'))
    #         buf = io.BytesIO(s)
    #         img = Image.open(buf)
    #         return img
    #     except:
    #         return None

    def to_internal_value(self, data):
        decode_data = data.get('image')
        image_data = b64decode(decode_data.split(',')[1])
        image = ContentFile(image_data, 'image.jpg')
        author = self.context.get('request').user
        cooking_time = data.get('cooking_time')
        is_favorited = data.get('is_favorited')
        is_in_shopping_cart = data.get('is_in_shopping_cart')
        name = data.get('name')
        ingredients = data.get('ingredients')
        tags = data.get('tags')


        # Perform the data validation.
        if name:
            if Recipe.objects.filter(name=name).exists():
                raise serializers.ValidationError({
                'name': 'Рецепт с таким именем уже существует'
            })
        else:
            raise serializers.ValidationError({
                'name': 'Это обязательное поле.'
            })
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Это обязательное поле'
            })
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Это обязательное поле'
            })
        if not image:
            raise serializers.ValidationError({
                'image': 'Это обязательное поле.'
            })
        if not author:
            raise serializers.ValidationError({
                'author': 'Это обязательное поле.'
            })
        if not cooking_time:
            raise serializers.ValidationError({
                'cooking_time': 'Это обязательное поле.'
            })
        if not is_favorited:
            is_favorited = False
        if not is_in_shopping_cart:
            is_in_shopping_cart = False

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        return {
            'name': name,
            'ingredients': ingredients,
            'tags': tags,
            'image': image,
            'author': author,
            'cooking_time': cooking_time,
            'is_favorited': is_favorited,
            'is_in_shopping_cart': is_in_shopping_cart
        }

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data =validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            amount = ingredient_data['amount']
            current_ingredient, status = Ingredient.objects.get_or_create(
                pk=ingredient_data['id']
            )
            IngredientProperty.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        for tag_data in tags_data:
            TagProperty.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(pk=tag_data)
            )
        return recipe
