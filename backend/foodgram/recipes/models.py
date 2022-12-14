from django.db import models
# from django.contrib.auth import get_user_model
from foodgram.settings import COLOR_CHOICES, TAG_CHOICES
# from user.models import User
from foodgram.settings import AUTH_USER_MODEL

User = AUTH_USER_MODEL
# User = get_user_model()

class Ingredient(models.Model):
    """ Описание модели Ингредиент """
    name = models.CharField(
        max_length=128,
        blank=False,
        db_index=True,
        verbose_name='Название',
        help_text='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=16,
        blank=False,
        verbose_name='Единица измерения',
        help_text='Единица измерения ингредиента'
    )
    # amount = models.PositiveSmallIntegerField(
    #     blank=False,
    #     verbose_name='Количество',
    #     help_text='Количество ингредиента'
    # )
    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    """ Описание модели Tag """

    name = models.CharField(
        max_length=64,
        unique=True,
        blank=False,
        choices=TAG_CHOICES,
        verbose_name='Название',
        help_text='Название тега'
    )
    color = models.CharField(
        max_length=64,
        unique=True,
        blank=False,
        default=None,
        verbose_name='Цвет',
        help_text='Цвет тега'
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        blank=False,
        db_index=True,
        verbose_name='slug',
        help_text='slug тега'
    )

    def save(self, *args, **kwargs) -> None: # Сделать анотирование !!!!
        # print(self.slug)
        self.color = COLOR_CHOICES[self.slug]
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    
    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """ Описание модели рецепт """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False,
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    name = models.CharField(
        max_length=128,
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
    ingredients = models.ManyToManyField(
        Ingredient,
        # on_delete=models.CASCADE,
        through='IngredientProperty',
        blank=False,
        verbose_name='Ингредиент',
        help_text='Ингредиент рецепта'
    )
    tag = models.ManyToManyField(
        Tag,
        through='TagProperty',
        verbose_name='Тег',
        help_text='Тег рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
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


class IngredientProperty(models.Model):
    """ Описание модели свойства ингредиента """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_property'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_property',
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name='Количество',
        help_text='Количество ингредиента'
    )

    class Meta:
        verbose_name = 'Свойство ингредиент'
        verbose_name_plural = 'Свойства ингредиентов'

    def __str__(self):
        return f'{self.ingredient}'


class TagProperty(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = 'Свойство тега'
        verbose_name_plural = 'Свойства тега'

    def __str__(self):
        return f'{self.tag}'