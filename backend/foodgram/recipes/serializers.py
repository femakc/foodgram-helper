from rest_framework import serializers, exceptions, status
from .models import Tag, Recipe, Ingredient
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


# class IngredientNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ingredient
#         fields = ['name']


class IngredientsSerializer(serializers.ModelSerializer):
    # name = IngredientNameSerializer()
    # measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = '__all__'



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

    # def decodeDesignImage(self, s):
    #     try:
    #         s = base64.b64decode(s.encode('UTF-8'))
    #         buf = io.BytesIO(s)
    #         img = Image.open(buf)
    #         return img
    #     except:
    #         return None

    def to_internal_value(self, data):
        # print(data)
        # print(self.context['request'].user)
        decode_data = data.get('image')
        # image = self.decodeDesignImage(decode_data.split(',')[1])
        image_data = b64decode(decode_data.split(',')[1])
        image = ContentFile(image_data, 'image.jpg')
        author = self.context.get('request').user
        cooking_time = data.get('cooking_time')
        is_favorited = data.get('is_favorited')
        is_in_shopping_cart = data.get('is_in_shopping_cart')

        # Perform the data validation.
        if not image:
            raise serializers.ValidationError({
                'image': 'Это обязательное поле.'
            })
        if not author:
            raise serializers.ValidationError({
                'author': 'Это обязательное поле.'
            })
        # if author.get_user_permissions == 'AnonymousUser':
        #     raise serializers.ValidationError({
        #         'author': 'AnonymousUser не может создать рецепт'
        #     })
        if not cooking_time:
            raise serializers.ValidationError({
                'cooking_time': 'Это обязательное поле.'
            })
        if not is_favorited:
            is_favorited = False
        if not is_in_shopping_cart:
            is_in_shopping_cart = False
        # if len(player_name) > 10:
        #     raise serializers.ValidationError({
        #         'player_name': 'May not be more than 10 characters.'
        #     })

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        return {
            'image': image,
            'author': author,
            'cooking_time': cooking_time,
            'is_favorited': is_favorited,
            'is_in_shopping_cart': is_in_shopping_cart
        }
    # def create(self, validated_data):
    #     tracks_data = validated_data.pop('tracks')
    #     album = Album.objects.create(**validated_data)
    #     for track_data in tracks_data:
    #         Track.objects.create(album=album, **track_data)
    #     return album
