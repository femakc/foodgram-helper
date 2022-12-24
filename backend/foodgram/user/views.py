from django.contrib.auth.hashers import make_password
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import mixins

from api.permissions import IsOwnerOnly
from api.serializers import (SetPasswordSerializer,
                             UserSerializer, UsersSerializer,
                             UserSubscribtionsSerializer)
from recipes.models import Recipe

from .models import Follow, User


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
        is_user = User.objects.filter(username=request.user).exists()
        user = User.objects.get(username=request.user)
        serializer = SetPasswordSerializer(
                user,
                data=request.data
            )
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
        # if User.objects.filter(pk=pk).exists():
        # if get_object_or_404(User, pk=pk):
        user = request.user
        # author = User.objects.get(pk=pk)
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
        elif request.method == 'DELETE' and Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            Follow.objects.get(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'User + Author ошибка модели Follow',
            status=status.HTTP_400_BAD_REQUEST
        )
        # return Response(
        #     "Нет такого автора !",
        #     status=status.HTTP_400_BAD_REQUEST
        # )


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
