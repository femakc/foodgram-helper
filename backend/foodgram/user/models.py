from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

from foodgram.settings import ROLES_CHOICES


class UserManager(BaseUserManager):
    """ Manager для создания User. """

    def create_user(self, username, email, password=None, **extra_fields):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('Пользователи должны иметь имя пользователя.')

        if email is None:
            raise TypeError('пользователи должны иметь email.')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создаём суперпользователя. """
        if password is None:
            raise TypeError('У Суперпользователя должен быть пароль.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ Модель пользователя"""

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
    first_name = models.CharField(
        max_length=150,
        blank=False,
        default='--пусто--',
        verbose_name='Имя',
        help_text='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        default='--пусто--',
        verbose_name='Фамилия',
        help_text='Фамилия пользователя'
    )
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
        return self.username

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"

    def get_short_name(self):
        return self.username


class Follow(models.Model):
    """ Модель подписки на Авторов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
        help_text='тот кто подписывается ',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор рецепта",
        help_text='тот на кого подписываются',
    )

    def __str__(self):
        return "Подписка на автора"
