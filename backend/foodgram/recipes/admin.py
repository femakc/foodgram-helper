from django.contrib import admin

from .models import Recipe, Ingredient, IngredientProperty, Tag

class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'author',
        'name',
        'image',
        'text',
        # 'ingredient',  как отобразить ManyToMany в админке
        # 'tag',
        'cooking_time'
    ]
    search_fields = ['text']
    list_filter = ['pub_date']
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
    ]
    search_fields = ['name']
    # list_filter = ['pub_date']
    # empty_value_display = '-пусто-'


class IngredientPropertyAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'measurement_unit',
        'amount',
    ]
    # search_fields = ['text']
    # list_filter = ['pub_date']
    # empty_value_display = '-пусто-'

class TagAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
        'color',
        'slug'
    ]
    prepopulated_fields = {"slug": ("name",)}
    # search_fields = ['name']

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientProperty, IngredientPropertyAdmin)
admin.site.register(Tag, TagAdmin)
