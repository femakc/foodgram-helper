from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'username',
        'email',
        'password',
        'first_name',
        'is_active',
        'is_staff',
        'last_name',
        'created_at'
    ]
    search_fields = ['email']
    list_filter = ['created_at']
    empty_value_display = '-пусто-'

admin.site.register(User, UserAdmin)

