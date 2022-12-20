from rest_framework import status, viewsets
from rest_framework.viewsets import mixins
# from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from api.permissions import IsAdminRole, IsOwnerOnly
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView
from .models import User, Follow
from recipes.models import Recipe
from rest_framework_simplejwt.views import TokenRefreshView
from  django.contrib.auth.hashers import make_password
from api.serializers import (RegistrationSerializer, UserSerializer,
                            TokenSerializer, SetPasswordSerializer, UserSubscribtionsSerializer,
                            FollowSerializer, UsersSerializer)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
# from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count


class APILogoutView(APIView): # Проверить как работает logout
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # try:
        #     # refresh_token = request.data["refresh_token"]
        #     refresh_token = self.request.data.get('refresh_token')
        #     token = RefreshToken(refresh_token)
        #     token.blacklist()

        #     return Response(status=status.HTTP_205_RESET_CONTENT)
        # except Exception as e:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # TokenRefreshView
        # if self.request.data.get('all'):
        # token: OutstandingToken
        for token in OutstandingToken.objects.filter(user=request.user):
            _, _ = BlacklistedToken.objects.get_or_create(token=token)
        return Response(status=status.HTTP_204_NO_CONTENT)
        # refresh_token = self.request.data.get('refresh_token')
        # token = RefreshToken(token=refresh_token)
        # token.blacklist()
        # return Response({"status": "OK, goodbye"})


class GetToken(TokenObtainPairView):
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class UsersVievSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet
):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UsersSerializer
        else:
            return UserSerializer


class UserVievSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Обработчик запросов к модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    # search_fields = ['username']
    # lookup_field = "username"

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsOwnerOnly],
        # name='me'
    )
    def me(self, request, pk=None):
        data = UserSerializer(request.user, many=False).data
        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        # name='set_password'
    )
    def set_password(self, request):
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        user = User.objects.get(username=request.user)
        serializer = SetPasswordSerializer(
                user,
                data=request.data
            )
        serializer.is_valid(raise_exception=True)
        if user.check_password(current_password):
            serializer.save(password=make_password(new_password))
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response("Не верно введен current_password", status=status.HTTP_401_UNAUTHORIZED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        if User.objects.filter(pk=pk).exists():
            user = request.user
            author = User.objects.get(pk=pk)
            if request.method == 'POST' and user != author: # добавить проверку подписки на самого себя !!!!!!
                follow_model = Follow.objects.get_or_create(user=user, author=author)
                # serializer = FollowSerializer(follow_model[0], data=request.data, partial=True)
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
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            elif request.method == 'DELETE' and Follow.objects.filter(user=user, author=author).exists():
                Follow.objects.get(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response('User + Author ошибка модели Follow', status=status.HTTP_400_BAD_REQUEST)
        return Response("Нет такого автора !", status=status.HTTP_400_BAD_REQUEST)
       


class UserSubscribtionsViewSet(viewsets.ModelViewSet):
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
        # return Response(serializer.data, status=status.HTTP_200_OK)
        return self.get_paginated_response(serializer.data)


# class UserSubscribeViewSet(viewsets.ModelViewSet):
#     # permission_classes = [IsOwnerPatch]
#     queryset = User.objects.filter(pk=2)
#     serializer_class = UserSerializer

#     def create(self, request, author_id):
#         print(author_id)
#         serializer = UserSerializer
#         serializer.is_valid()
#         serializer.seve()
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
