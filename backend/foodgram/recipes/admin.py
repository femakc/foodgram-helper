from django.contrib import admin

from .models import Ingredient, IngredientProperty, Recipe, Tags, UserShopCart


class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'author',
        'name',
        'image',
        'text',
        # 'ingredient',  как отобразить ManyToMany в админке
        # 'tags',
        'cooking_time'
    ]
    search_fields = ['text']
    list_filter = ['pub_date']
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
        # 'measurement_unit',
        # 'amount'
    ]
    search_fields = ['name']
    # list_filter = ['pub_date']
    # empty_value_display = '-пусто-'


class IngredientPropertyAdmin(admin.ModelAdmin):
    list_display = [
        'recipe',
        'ingredient',
        'amount'
    ]
#     # search_fields = ['text']
#     empty_value_display = '-пусто-'


class TagsAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
        'color',
        'slug'
    ]
    prepopulated_fields = {"slug": ("name",)}
    # search_fields = ['name']


class ShopListAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'recipe',
        'pub_date'
    ]


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientProperty, IngredientPropertyAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(UserShopCart, ShopListAdmin)
