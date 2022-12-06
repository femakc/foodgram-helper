from django.urls import include, path
# from recipes.views import RecipeViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

# router.register('recipes', RecipeViewSet, basename='recipe')


app_name = "api"

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
]