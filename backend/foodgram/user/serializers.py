from rest_framework import serializers, exceptions, status
from rest_framework.validators import UniqueTogetherValidator
from collections import OrderedDict
from  django.contrib.auth.hashers import make_password

from .models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['auth_token'] = str(refresh.access_token)
        del data['refresh']
        del data['access']

        return data

class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """
    # email = serializers.EmailField()
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
            # if username.exists():
            #     send_message(data['username'])
            # else:
            #     raise serializers.ValidationError(
            #         "user не соответствует email"
            #     )
        else:
            username = User.objects.filter(username=data['username'])
            if username.exists():
                raise serializers.ValidationError(
                    "email не соответствует User "
                )

        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели User."""
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    def create(self, validated_data):
        print(validated_data)
        password = validated_data['password']
        validated_data['password'] = make_password(password)
        print(validated_data)

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
        # exclude = ['password']
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email'),
                message='Имя пользователя или email уже используются'
            )
        ]


class SetPasswordSerializer(serializers.ModelSerializer):
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
