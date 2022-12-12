from django.urls import include, path
# from recipes.views import RecipeViewSet
from rest_framework.routers import DefaultRouter
from user.views import UserVievSet, GetToken, UsersVievSet, APILogoutView
from recipes.views import TagsViewSet, RecipeVievSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView



router = DefaultRouter()

# router.register('recipes', RecipeViewSet, basename='recipe')
router.register(r'users', UsersVievSet, basename='users')
router.register(r'users', UserVievSet, basename='users')
router.register(r'users/set_password/', UsersVievSet, basename='users')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipeVievSet, basename='recipes')




app_name = "api"

urlpatterns = [
    # path('users/', RegistrationAPIView.as_view())
    path('', include(router.urls)),
    # path('users/', UsersApiView.as_view()),
    # path('users/me/', UserApiView.as_view()),
    # path('users/<str:user_id>/', UsersVievSet.as_view({'get': 'list'})),
    # path('', include('djoser.urls')),
    path('auth/token/login/', GetToken.as_view(), name='login_token'),
    path('auth/token/logout/', APILogoutView.as_view(), name='logout_token'),
    # path('auth/token/logout/', User_logout),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]