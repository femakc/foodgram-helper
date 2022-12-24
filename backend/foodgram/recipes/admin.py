from django.contrib import admin

from .models import Ingredients, IngredientProperty, Recipe, Tags, UserShopCart

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time'
    ]
    search_fields = ['text']
    # list_filter = ['pub_date']
    empty_value_display = '-пусто-'

@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
    ]
    search_fields = ['name']

@admin.register(IngredientProperty)
class IngredientPropertyAdmin(admin.ModelAdmin):
    list_display = [
        'recipe',
        'ingredient',
        'amount'
    ]

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
        'color',
        'slug'
    ]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(UserShopCart)
class ShopListAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'recipe',
        'pub_date'
    ]


# admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(Ingredient, IngredientAdmin)
# admin.site.register(IngredientProperty, IngredientPropertyAdmin)
# admin.site.register(Tags, TagsAdmin)
# admin.site.register(UserShopCart, ShopListAdmin)
