from django.contrib import admin

from .models import Follow, User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = [
        'pk',
        'username',
        'email',
        'first_name',
        'is_active',
        # 'is_staff',
        'last_name',
        'is_subscribed',
        # 'role',
        # 'created_at'
    ]
    search_fields = ['email']
    # list_filter = ['created_at']
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
