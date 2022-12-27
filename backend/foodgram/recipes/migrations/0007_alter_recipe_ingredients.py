# Generated by Django 4.1.4 on 2022-12-27 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_ingredientproperty_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Ингредиент рецепта', related_name='resipe_ingredients', through='recipes.IngredientProperty', to='recipes.ingredients', verbose_name='Ингредиент'),
        ),
    ]