import os

from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import mixins
from .filters import Filter
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerialzer,
                             ShopingCardSerializer, TagsSerializer, CreateRecipeSerialzer)
from foodgram.settings import BASE_DIR
from recipes.utilits import make_send_file
# from . import serializers

# from django.shortcuts import get_list_or_404, get_object_or_404

from recipes.models import (
    Ingredients,
    IngredientProperty,
    Recipe,
    Tags,
    UserShopCart,
    Favorite
)


class TagsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """ Обработчик модели Tags """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AllowAny,]
    pagination_class = None


class IngredientVievSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """ Обработчик модели Ingredient """
    queryset = Ingredients.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name',]


class RecipeVievSet(viewsets.ModelViewSet):
    """ Обработчик модели Recipe """
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Filter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerialzer
        return CreateRecipeSerialzer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        new_serializer = CreateRecipeSerialzer(
            recipe,
            context={'request': request}
        )
        return Response(new_serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """ Скачать файл со списком ингредиентов """
        ingredient = IngredientProperty.objects.filter(
            recipe__usershopcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        file_data = make_send_file(ingredient)
        return HttpResponse(file_data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None, cart_or_fav=None):
        """ Обработка запросов на добавление в избранное и корзину """
               
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shop_cart = UserShopCart.objects.filter(
            user=user,
            recipe=recipe
        )

        if request.method == "POST":
            if cart_or_fav == 'favorite':
                Favorite.objects.create(
                user=user,
                recipe=recipe
                )
            UserShopCart.objects.create(
            user=user,
            recipe=recipe
            )
            serializer = ShopingCardSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        elif request.method == 'DELETE':
            # UserShopCart.objects.get(user=user, recipe=recipe).delete()
            in_shop_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='favorite'
    )
    def favorite(self, request, pk=None):
        """ обработчик запросов по url .../favorite/"""
        favorite = 'favorite' 
        return self.shopping_cart(request, pk, favorite)
