import jwt

from datetime import datetime, timedelta

from django.conf import settings 
from django.contrib.auth.models import (
	AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from django.db import models

from foodgram.settings import ROLES_CHOICES

class UserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User (для демонстрации).
    """

    def create_user(self, username, email, password=None, **extra_fields):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')
        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        verbose_name='Уникальный юзернейм ',
        help_text='Логин пользователя'
    )
    email = models.EmailField(
        db_index=True,
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты',
        help_text='email пользователя'
    )
    # password = models.CharField(
    #     max_length=150,
    #     verbose_name='Пароль',
    #     help_text='Пароль пользователя'
    # )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Фамилия пользователя'
    )
    # Когда пользователь более не желает пользоваться нашей системой, он может
    # захотеть удалить свой аккаунт. Для нас это проблема, так как собираемые
    # нами данные очень ценны, и мы не хотим их удалять :) Мы просто предложим
    # пользователям способ деактивировать учетку вместо ее полного удаления.
    # Таким образом, они не будут отображаться на сайте, но мы все еще сможем
    # далее анализировать информацию.
    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    is_subscribed = models.BooleanField(default=False)

    role = models.CharField(
        max_length=32,
        choices=ROLES_CHOICES,
        default='user',
        verbose_name='Роль пользователя',
        help_text='роль'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        """ Строковое представление модели (отображается в консоли) """
        return self.username

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"

    def get_short_name(self):
        return self.username

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')


# from django.contrib.auth import get_user_model

# class EmailBackend(object):
#     """
#     Custom Email Backend to perform authentication via email
#     """
#     def authenticate(self, username=None, password=None):
#         user_model = get_user_model() 
#         try:
#             user = user_model.objects.get(email=username)
#             if user.check_password(password): # check valid password
#                 return user # return user to be authenticated
#         except user_model.DoesNotExist: # no matching user exists 
#             return None 

#     def get_user(self, user_id):
#         user_model = get_user_model() 
#         try:
#             return user_model.objects.get(pk=user_id)
#         except user_model.DoesNotExist:
#             return None

# # settings.py
# AUTHENTICATION_BACKENDS = (
#     'my_app.backends.EmailBackend', 
#     ... 
#     )
