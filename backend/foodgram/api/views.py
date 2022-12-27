from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, IngredientProperty, Ingredients, Recipe,
                            Tags, UserShopCart)
from recipes.utilits import make_send_file
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import mixins
from user.models import Follow, User

from . import serializers
from .filters import CustomSearchFilter, Filter
from .permissions import IsAuthorOrReadOnly, IsOwnerOnly
from .serializers import (CreateRecipeSerialzer, IngredientsSerializer,
                          RecipeSerialzer, SetPasswordSerializer,
                          ShopingCardSerializer, TagsSerializer,
                          UserSerializer, UsersSerializer,
                          UserSubscribtionsSerializer)


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


class IngredientVievSet(viewsets.ReadOnlyModelViewSet):
    """ Обработчик модели Ingredient """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


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
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        new_serializer = CreateRecipeSerialzer(
            recipe,
            context={'request': request}
        )
        return Response(new_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        new_serializer = serializers.RecipeSerialzer(
            recipe,
            context={'request': request},
            partial=partial
        )
        return Response(new_serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

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
        return HttpResponse(
            file_data,
            content_type='text/plain',
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        """ Обработка запросов на добавление в избранное и корзину """

        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shop_cart = UserShopCart.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == "POST":
            UserShopCart.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            serializer = ShopingCardSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
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
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(
            user=user,
            recipe=recipe
        )

        if request.method == "POST":
            Favorite.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            serializer = ShopingCardSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UsersVievSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """Обработчик запросов к модели User доступен для всех. """
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UsersSerializer
        return UserSerializer


class UserVievSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Обработчик запросов к модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsOwnerOnly],
        name='me'
    )
    def me(self, request, pk=None):
        data = UserSerializer(request.user, many=False).data
        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        name='set_password'
    )
    def set_password(self, request):
        """ Смена пароля """
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        user = User.objects.get(username=request.user)
        serializer = SetPasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(current_password):
            serializer.save(password=make_password(new_password))
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            "Не верно введен current_password",
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='subscribe'
    )
    def subscribe(self, request, pk=None):
        """ Подписка на авторов рецепта"""

        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST' and user != author:
            Follow.objects.get_or_create(user=user, author=author)
            serializer = UserSubscribtionsSerializer(
                author,
                data=request.data,
                partial=True,
                context={
                    'author': author,
                    'user': user
                }
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE' and Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            Follow.objects.get(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'User + Author ошибка модели Follow',
            status=status.HTTP_400_BAD_REQUEST
        )


class UserSubscribtionsViewSet(viewsets.ModelViewSet):
    """ Список авторов на которых подписан пользователь """
    permission_classes = [IsOwnerOnly]

    def list(self, request):
        user = request.user
        authors = Follow.objects.select_related('author').filter(user=user)
        recipes = Recipe.objects.filter(author__in=authors.values('author_id'))
        queryset = User.objects.filter(pk__in=authors.values('author_id'))
        page = self.paginate_queryset(queryset)
        serializer = UserSubscribtionsSerializer(page, many=True, context={
            'recipes': recipes,
            'queryset': queryset,
            'user': user
        }
        )
        return self.get_paginated_response(serializer.data)
