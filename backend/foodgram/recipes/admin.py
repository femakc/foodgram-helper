from django.contrib import admin

from .models import Recipe

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
    list_filter = ['pub_date']
    empty_value_display = '-пусто-'

admin.site.register(Recipe, RecipeAdmin)