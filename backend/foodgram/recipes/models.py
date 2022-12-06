from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Recipe(models.Model):
    """ Описание модели рецепт """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        # unique=True,
        blank=False,
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    name = models.CharField(
        max_length=128,
        unique=True,
        blank=False,
        verbose_name='Название',
        help_text='Название рецепта'
    )
    image = models.ImageField(
        blank=True, # для тестов True, на прод поставить False
        verbose_name='Изображение',
        help_text='Изображение рецепта'
    )
    text = models.CharField(
        max_length=1000,
        blank=False,
        verbose_name='Описание',
        help_text='Описание рецепта'
    )
    # ingredients = отношение многие ко многим
    # tags = отношение многие ко многоим
    cooking_time = models.IntegerField(
        blank=False,
        verbose_name='Время приготовления',
        help_text='Время приготовления рецепта'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания рецепта'
    )
    is_favorited = models.BooleanField()
    is_in_shopping_cart = models.BooleanField()

    class Meta:
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'
        ordering = ['pub_date']

    def __str__(self):
        return f'{self.name}'
