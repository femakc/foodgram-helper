from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from foodgram.common import COLOR_CHOICES, TAG_CHOICES
from foodgram.settings import AUTH_USER_MODEL

User = AUTH_USER_MODEL


class Ingredients(models.Model):
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

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Tags(models.Model):
    """ Описание модели Tags """

    name = models.CharField(
        max_length=64,
        unique=True,
        blank=False,
        choices=TAG_CHOICES,
        verbose_name='Название',
        help_text='Название тега'
    )
    color = ColorField(
        unique=True,
        verbose_name='Цветовой HEX-код'
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        blank=False,
        db_index=True,
        verbose_name='slug',
        help_text='slug тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        self.color = COLOR_CHOICES[self.slug]
        return super().save(*args, **kwargs)


class Recipe(models.Model):
    """ Описание модели Recipe """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
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
        blank=False,
        upload_to='recipes/images/',
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
        Ingredients,
        through='IngredientProperty',
        blank=False,
        verbose_name='Ингредиент',
        help_text='Ингредиент рецепта'
    )
    tags = models.ManyToManyField(
        Tags,
        through='TagsProperty',
        related_name='tags',
        verbose_name='Тег',
        help_text='Тег рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name='Время приготовления',
        help_text='Время приготовления рецепта',
        default=0,
        validators=[MinValueValidator(
            1,
            'Время приготовления должно быть больше 1 минуты.'
        )]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания рецепта'
    )

    class Meta:
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe_author_name'
            )
        ]

    def __str__(self):
        return f'{self.name}'


class IngredientProperty(models.Model):
    """ Описание модели свойства ингредиента """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='resipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name='Количество',
        help_text='Количество ингредиента',
        validators=[MinValueValidator(1, 'Значение должно быть больше нуля.')]
    )

    class Meta:
        verbose_name = 'Свойство ингредиент'
        verbose_name_plural = 'Свойства ингредиентов'

        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_constrain'
            )
        ]

    def __str__(self):
        return f'{self.ingredient}'


class TagsProperty(models.Model):
    """ Описание модели свойства тега"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    tags = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Свойство тега'
        verbose_name_plural = 'Свойства тега'

    def __str__(self):
        return f'{self.tags}'


class UserShopCart(models.Model):
    """ Модель корзины покупок """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_cart',
        blank=False,
        verbose_name='Пользователь',
        help_text='Пользователь корзины'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='usershopcart',
        verbose_name='рецепт',
        help_text='рецепт пользователя'
    )
    # pub_date = models.DateField(
    #     auto_now_add=True,
    #     verbose_name='Дата добавления',
    #     help_text='Дата добавления рецепта'
    # )

    class Meta:
        verbose_name = 'Список избранных'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shop_cart'
            )
        ]

    def __str__(self):
        return f"{self.user} добавил в список покупок {self.recipe}"


class Favorite(models.Model):
    """ Модель корзины покупок """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        blank=False,
        verbose_name='Пользователь',
        help_text='Пользователь корзины'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='рецепт',
        help_text='рецепт пользователя'
    )
    # pub_date = models.DateField(
    #     auto_now_add=True,
    #     verbose_name='Дата добавления',
    #     help_text='Дата добавления рецепта'
    # )

    class Meta:
        verbose_name = 'Список избранных рецептов'
        verbose_name_plural = 'Списки избранных рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f"{self.user} добавил в список избранных рецептов {self.recipe}"
