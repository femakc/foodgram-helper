# Generated by Django 4.1.4 on 2022-12-25 19:56

import colorfield.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateField(auto_now_add=True, help_text='Дата добавления рецепта', verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Список избранных рецептов',
                'verbose_name_plural': 'Списки избранных рецептов',
            },
        ),
        migrations.CreateModel(
            name='IngredientProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(help_text='Количество ингредиента', verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Свойство ингредиент',
                'verbose_name_plural': 'Свойства ингредиентов',
            },
        ),
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Название ингредиента', max_length=128, verbose_name='Название')),
                ('measurement_unit', models.CharField(help_text='Единица измерения ингредиента', max_length=16, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название рецепта', max_length=128, verbose_name='Название')),
                ('image', models.ImageField(help_text='Изображение рецепта', upload_to='recipes/images/', verbose_name='Изображение')),
                ('text', models.CharField(help_text='Описание рецепта', max_length=1000, verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(default=0, help_text='Время приготовления рецепта', validators=[django.core.validators.MinValueValidator(1, 'Время приготовления должно быть больше 1 минуты.')], verbose_name='Время приготовления')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания рецепта')),
            ],
            options={
                'verbose_name': 'Рецепты',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('breakfast', 'Завтрак'), ('lunch', 'обед'), ('dinner', 'ужин')], help_text='Название тега', max_length=64, unique=True, verbose_name='Название')),
                ('color', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=None, unique=True, verbose_name='Цветовой HEX-код')),
                ('slug', models.SlugField(help_text='slug тега', max_length=32, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='TagsProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Свойство тега',
                'verbose_name_plural': 'Свойства тега',
            },
        ),
        migrations.CreateModel(
            name='UserShopCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateField(auto_now_add=True, help_text='Дата добавления рецепта', verbose_name='Дата добавления')),
                ('recipe', models.ForeignKey(help_text='рецепт пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='usershopcart', to='recipes.recipe', verbose_name='рецепт')),
            ],
            options={
                'verbose_name': 'Список избранных',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
    ]
