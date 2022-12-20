from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import IngredientVievSet, RecipeVievSet, TagsViewSet
from user.views import (UserSubscribtionsViewSet,
                        UsersVievSet, UserVievSet)

router = DefaultRouter()

router.register(
    r'users/subscriptions',
    UserSubscribtionsViewSet,
    basename='users/subscriptions/'
)
router.register(r'ingredients', IngredientVievSet, basename='ingredients')
router.register(r'users', UserVievSet, basename='users')
router.register(r'users', UsersVievSet, basename='users')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipeVievSet, basename='recipes')

app_name = "api"

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
