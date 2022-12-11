# Generated by Django 3.0 on 2022-12-06 19:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название рецепта', max_length=128, unique=True, verbose_name='Название')),
                ('image', models.ImageField(blank=True, help_text='Изображение рецепта', upload_to='', verbose_name='Изображение')),
                ('text', models.CharField(help_text='Описание рецепта', max_length=1000, verbose_name='Описание')),
                ('cooking_time', models.IntegerField(help_text='Время приготовления рецепта', verbose_name='Время приготовления')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания рецепта')),
                ('is_favorited', models.BooleanField()),
                ('is_in_shopping_cart', models.BooleanField()),
                ('author', models.ForeignKey(help_text='Автор рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Рецепты',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['pub_date'],
            },
        ),
    ]