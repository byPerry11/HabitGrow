from django.urls import path
from .views import RegistroUsuarioView
from .api_views import RegisterAPIView, LoginAPIView
from .auth_google import GoogleLoginAPIView

app_name = 'users'

urlpatterns = [
    # Template View
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    
    # API endpoints - Autenticación clásica
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),

    # API endpoints - Google OAuth2
    path('api/google-auth/', GoogleLoginAPIView.as_view(), name='api_google_auth'),
]
