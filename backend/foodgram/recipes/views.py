import os
from foodgram.settings import BASE_DIR
from django.shortcuts import render, get_object_or_404, HttpResponse
from rest_framework import status, viewsets
from rest_framework.viewsets import mixins
from rest_framework.response import Response
from .models import Tags, Recipe, UserShopCart, IngredientProperty, UserFavorite, Ingredient
from api.serializers import TagsSerializer, RecipeSerialzer, ShopingCardSerializer, IngredientSerializer
from api.permissions import IsAuthorOrReadOnly
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum



class TagsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AllowAny,]
    pagination_class = None


class RecipeVievSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerialzer
    permission_classes = [IsAuthorOrReadOnly,]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        ingredient = IngredientProperty.objects.filter(
            recipe__usershopcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'          
        ).annotate(amount=Sum('amount'))

        shop_list_file = open('shop_list_file.txt', 'w')
        for i in ingredient:
            shop_list_file.write(f'\n')
            for key, value in i.items():
                shop_list_file.write(f'{key} - {value}\n')
        shop_list_file.close()

        my_file = os.path.join(BASE_DIR, 'shop_list_file.txt')

        with open(my_file, 'r') as f:
           file_data = f.read()
        response = HttpResponse(file_data, status=status.HTTP_200_OK)
        return response
        
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        """ обработчик запросов по url .../shopping_cart/"""
        if Recipe.objects.filter(pk=pk).exists():
            user = request.user
            recipe = Recipe.objects.get(pk=pk)
            UserShopCart.objects.get_or_create(user=user, recipe=recipe)
            request.data['name'] = recipe.name
            request.data['cooking_time'] = recipe.cooking_time
            if request.method == "POST":
                recipe.is_in_shopping_cart = True
                request.data['is_in_shopping_cart'] = recipe.is_in_shopping_cart
                serializer = ShopingCardSerializer(recipe, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if request.method == 'DELETE':
                UserShopCart.objects.get(user=user, recipe=recipe).delete()
                # recipe.is_in_shopping_cart = False   
                # request.data['is_in_shopping_cart'] = recipe.is_in_shopping_cart
                # serializer = ShopingCardSerializer(recipe, data=request.data)
                # serializer.delete()
                # if serializer.is_valid():
                #     serializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
                # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        return Response({'errors': 'нет такого рецепта'}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='favorite'
    )
    def favorite(self, request, pk=None):
        """ обработчик запросов по url .../favorite/"""
        if Recipe.objects.filter(pk=pk).exists():
            user = request.user
            recipe = Recipe.objects.get(pk=pk)
            UserFavorite.objects.get_or_create(user=user, recipe=recipe)
            request.data['name'] = recipe.name
            request.data['cooking_time'] = recipe.cooking_time
            if request.method == "POST":
                recipe.is_favorited = True
                request.data['is_favorited'] = recipe.is_favorited
                serializer = ShopingCardSerializer(recipe, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if request.method == 'DELETE':
                UserFavorite.objects.get(user=user, recipe=recipe).delete()
                # recipe.is_in_shopping_cart = False   
                # request.data['is_in_shopping_cart'] = recipe.is_in_shopping_cart
                # serializer = ShopingCardSerializer(recipe, data=request.data)
                # serializer.delete()
                # if serializer.is_valid():
                #     serializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
                # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        return Response({'errors': 'нет такого рецепта'}, status=status.HTTP_400_BAD_REQUEST)


class IngredientVievSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = IngredientSerializer
    # реализовать поис по условию ! !!!!!!!!!!!!