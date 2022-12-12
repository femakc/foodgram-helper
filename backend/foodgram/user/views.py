from rest_framework import status, viewsets
from rest_framework.viewsets import mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .permissions import IsAdminRole, IsOwnerPatch
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView
from .models import User
from rest_framework_simplejwt import views
from  django.contrib.auth.hashers import make_password
from .serializers import (RegistrationSerializer, UserSerializer,
                            TokenSerializer, SetPasswordSerializer)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
# from rest_framework_simplejwt.tokens import RefreshToken
# from drf_yasg.utils import swagger_auto_schema


class APILogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # if self.request.data.get('all'):
        token: OutstandingToken
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
    serializer_class = UserSerializer


class UserVievSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Обработчик запросов к модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerPatch)
    # search_fields = ['username']
    # lookup_field = "username"

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, IsOwnerPatch]
    )
    def me(self, request, pk=None):
        data = UserSerializer(request.user, many=False).data
        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
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
    